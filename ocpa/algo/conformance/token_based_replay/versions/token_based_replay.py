import pm4py
# from pm4pymdl.algo.mvp.utils import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.objects.log.importer.mdl.factory import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.algo.discovery.mvp.projection import algorithm as projection_factory
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as sa_get
from pm4py.statistics.end_activities.log import get as ea_get
from pm4py.objects.conversion.dfg import converter as dfg_converter
from pm4py.algo.conformance.tokenreplay import algorithm as tr_factory
from pm4py.visualization.petrinet.util import performance_map
from pm4py.statistics.variants.log import get as variants_module
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import add_arc_from_to
from pm4py.objects.petri.utils import remove_place, remove_transition
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from copy import deepcopy
import uuid
import pandas as pd
import time
from statistics import median, mean
from pm4py.util.vis_utils import human_readable_stat

PARAM_ACTIVITY_KEY = pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY
MAX_FREQUENCY = float("inf")


def apply(ocpn, df, parameters=None):
    if parameters is None:
        parameters = {}

    allowed_activities = parameters["allowed_activities"] if "allowed_activities" in parameters else None
    debug = parameters["debug"] if "debug" in parameters else False

    df = succint_mdl_to_exploded_mdl(df)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    min_node_freq = parameters["min_node_freq"] if "min_node_freq" in parameters else 0
    min_edge_freq = parameters["min_edge_freq"] if "min_edge_freq" in parameters else 0

    df = clean_frequency(df, min_node_freq)
    df = clean_arc_frequency(df, min_edge_freq)

    if len(df) == 0:
        df = pd.DataFrame({"event_id": [], "event_activity": []})

    diag = dict()

    diag["act_freq"] = {}
    diag["arc_freq"] = {}
    diag["group_size_hist"] = {}
    diag["act_freq_replay"] = {}
    diag["group_size_hist_replay"] = {}
    diag["aligned_traces"] = {}
    diag["place_fitness_per_trace"] = {}
    diag["agg_statistics_frequency"] = {}
    diag["agg_performance_min"] = {}
    diag["agg_performance_max"] = {}
    diag["agg_performance_median"] = {}
    diag["agg_performance_mean"] = {}

    diff_log = 0
    diff_model = 0
    diff_token_replay = 0
    diff_performance_annotation = 0
    diff_basic_stats = 0

    persps = ocpn.object_types
    # when replaying streaming log, some objects are missing.
    persps = [x for x in persps if x in df.columns]

    for persp in persps:
        net, im, fm = ocpn.nets[persp]
        aa = time.time()
        if debug:
            print(persp, "getting log")
        log = projection_factory.apply(df, persp, parameters=parameters)
        if debug:
            print(len(log))

        if allowed_activities is not None:
            if persp not in allowed_activities:
                continue
            filtered_log = attributes_filter.apply_events(
                log, allowed_activities[persp])
        else:
            filtered_log = log
        bb = time.time()

        diff_log += (bb - aa)

        if debug:
            print(len(log))
            print(persp, "got log")

        cc = time.time()

        dd = time.time()

        diff_model += (dd - cc)

        if debug:
            print(persp, "got model")

        # Diagonstics - Activity Counting
        xx1 = time.time()
        activ_count = projection_factory.apply(
            df, persp, variant="activity_occurrence", parameters=parameters)
        if debug:
            print(persp, "got activ_count")
        xx2 = time.time()

        ee = time.time()
        variants_idx = variants_module.get_variants_from_log_trace_idx(log)
        # variants = variants_module.convert_variants_trace_idx_to_trace_obj(log, variants_idx)
        # parameters_tr = {PARAM_ACTIVITY_KEY: "concept:name", "variants": variants}
        if debug:
            print(persp, "got variants")

        aligned_traces, place_fitness_per_trace, transition_fitness_per_trace, notexisting_activities_in_model = tr_factory.apply(
            log, net, im, fm, parameters={"enable_pltr_fitness": True, "disable_variants": True})

        if debug:
            print(persp, "done tbr")
        element_statistics = performance_map.single_element_statistics(
            log, net, im, aligned_traces, variants_idx)

        if debug:
            print(persp, "done element_statistics")
        ff = time.time()

        diff_token_replay += (ff - ee)

        agg_statistics = aggregate_statistics(
            element_statistics)

        # if debug:
        #     print(persp, "done agg_statistics")

        # element_statistics_performance = performance_map.single_element_statistics(log, net, im, aligned_traces, variants_idx)

        # if debug:
        #     print(persp, "done element_statistics_performance")

        # gg = time.time()

        agg_performance_min = aggregate_statistics(
            element_statistics, measure="performance", aggregation_measure="min")
        agg_performance_max = aggregate_statistics(
            element_statistics, measure="performance", aggregation_measure="max")
        agg_performance_median = aggregate_statistics(
            element_statistics, measure="performance", aggregation_measure="median")
        agg_performance_mean = aggregate_statistics(
            element_statistics, measure="performance", aggregation_measure="mean")

        hh = time.time()

        diff_performance_annotation += (hh - ee)

        if debug:
            print(persp, "done agg_statistics_performance")

        group_size_hist = projection_factory.apply(
            df, persp, variant="group_size_hist", parameters=parameters)

        if debug:
            print(persp, "done group_size_hist")

        occurrences = {}
        for trans in transition_fitness_per_trace:
            occurrences[trans.label] = set()
            for trace in transition_fitness_per_trace[trans]["fit_traces"]:
                if not trace in transition_fitness_per_trace[trans]["underfed_traces"]:
                    case_id = trace.attributes["concept:name"]
                    for event in trace:
                        if event["concept:name"] == trans.label:
                            occurrences[trans.label].add(
                                (case_id, event["event_id"]))

        # len_different_ids = {}
        # for act in occurrences:
        #     len_different_ids[act] = len(set(x[1] for x in occurrences[act]))

        # eid_acti_count = {}
        # for act in occurrences:
        #     eid_acti_count[act] = {}
        #     for x in occurrences[act]:
        #         if not x[0] in eid_acti_count:
        #             eid_acti_count[act][x[0]] = 0
        #         eid_acti_count[act][x[0]] = eid_acti_count[act][x[0]] + 1
        #     eid_acti_count[act] = sorted(list(eid_acti_count[act].values()))

        ii = time.time()

        diff_basic_stats += (ii - hh) + (xx2-xx1)

        # Diagnostics on transitions
        diag["act_freq"][persp] = activ_count

        # diag["aligned_traces"][persp] = aligned_traces
        diag["place_fitness_per_trace"][persp] = place_fitness_per_trace
        diag["agg_statistics_frequency"][persp] = agg_statistics
        diag["agg_performance_min"][persp] = agg_performance_min
        diag["agg_performance_max"][persp] = agg_performance_max
        diag["agg_performance_median"][persp] = agg_performance_median
        diag["agg_performance_mean"][persp] = agg_performance_mean

        diag["arc_freq"][persp] = agg_statistics
        diag["group_size_hist"][persp] = group_size_hist
        # diag["act_freq_replay"][persp] = len_different_ids
        # diag["group_size_hist_replay"][persp] = eid_acti_count

    # diag["computation_statistics"] = {"diff_log": diff_log, "diff_model": diff_model,
    #                                   "diff_token_replay": diff_token_replay,
    #                                   "diff_performance_annotation": diff_performance_annotation,
    #                                   "diff_basic_stats": diff_basic_stats}

    # Transitions
    diag["replayed_act_freq"] = merge_act_freq(diag["act_freq"])
    merged_group_size_hist = merge_group_size_hist(diag["group_size_hist"])
    diag["agg_merged_group_size_hist"] = agg_merged_group_size_hist(
        merged_group_size_hist)
    diag["replayed_place_fitness"] = merge_place_fitness(
        diag["place_fitness_per_trace"])
    diag["replayed_performance_median"] = merge_agg_performance(
        diag["agg_performance_median"])
    diag["replayed_performance_mean"] = merge_agg_performance(
        diag["agg_performance_mean"])
    diag["replayed_performance_min"] = merge_agg_performance(
        diag["agg_performance_min"])
    diag["replayed_performance_max"] = merge_agg_performance(
        diag["agg_performance_max"])

    diag["replayed_arc_frequency"] = merge_replay(diag["arc_freq"])
    # Places

    return diag


def aggregate_statistics(statistics, measure="frequency", aggregation_measure=None):
    """
    Gets aggregated statistics

    Parameters
    ----------
    statistics
        Individual element statistics (including unaggregated performances)
    measure
        Desidered view on data (frequency or performance)
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use

    Returns
    ----------
    aggregated_statistics
        Aggregated statistics for arcs, transitions, places
    """
    aggregated_statistics = {}
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if measure == "frequency":
                freq = statistics[elem]["count"]
                aggregated_statistics[elem] = str(freq)
            elif measure == "performance":
                if statistics[elem]["performance"]:
                    aggr_stat = performance_map.aggregate_stats(
                        statistics, elem, aggregation_measure)
                    aggr_stat_hr = human_readable_stat(aggr_stat)
                    aggregated_statistics[elem] = aggr_stat_hr
        elif type(elem) is PetriNet.Transition:
            if measure == "frequency":
                if elem.label is not None:
                    freq = statistics[elem]["count"]
                    aggregated_statistics[elem] = elem.label + \
                        " (" + str(freq) + ")"
        elif type(elem) is PetriNet.Place:
            pass
    return aggregated_statistics


def merge_agg_performance(agg_performance):
    merged_agg_performance = dict()
    for persp in agg_performance:
        for el in agg_performance[persp]:
            merged_agg_performance[repr(el)] = agg_performance[persp][el]
    return merged_agg_performance


def merge_replay(replay):
    merged_replay = dict()
    for persp in replay.keys():
        for elem in replay[persp].keys():
            if type(elem) is PetriNet.Arc:
                merged_replay[elem.__repr__()] = replay[persp][elem]
    return merged_replay


def merge_place_fitness(place_fitness_per_trace):
    merged_place_fitness = dict()
    for persp in place_fitness_per_trace.keys():
        for pl in place_fitness_per_trace[persp]:
            merged_place_fitness[pl.name] = dict()
            merged_place_fitness[pl.name]['p'] = place_fitness_per_trace[persp][pl]['p']
            merged_place_fitness[pl.name]['r'] = place_fitness_per_trace[persp][pl]['r']
            merged_place_fitness[pl.name]['c'] = place_fitness_per_trace[persp][pl]['c']
            merged_place_fitness[pl.name]['m'] = place_fitness_per_trace[persp][pl]['m']
    return merged_place_fitness


def merge_act_freq(act_freq):
    merged_act_freq = dict()
    for persp in act_freq.keys():
        for act in act_freq[persp].keys():
            # persp_act_freq = {persp: act_freq[persp][act]}
            persp_act_freq = act_freq[persp][act]
            if act not in merged_act_freq.keys():
                merged_act_freq[act] = persp_act_freq
            else:
                continue
    return merged_act_freq


def merge_group_size_hist(group_size_hist):
    merged_group_size_hist = dict()
    for persp in group_size_hist.keys():
        for act in group_size_hist[persp].keys():
            persp_group_size_hist = {persp: group_size_hist[persp][act]}
            if act not in merged_group_size_hist.keys():
                merged_group_size_hist[act] = persp_group_size_hist
            else:
                merged_group_size_hist[act].update(persp_group_size_hist)
    return merged_group_size_hist


def agg_merged_group_size_hist(merged_group_size_hist):
    agg_merged_group_size_hist = dict()
    for act in merged_group_size_hist.keys():
        agg_merged_group_size_hist[act] = dict()
        # median
        agg_merged_group_size_hist[act]["median"] = dict()
        for persp in merged_group_size_hist[act].keys():
            agg_merged_group_size_hist[act]["median"][persp] = median(
                merged_group_size_hist[act][persp])
        # mean
        agg_merged_group_size_hist[act]["mean"] = dict()
        for persp in merged_group_size_hist[act].keys():
            agg_merged_group_size_hist[act]["mean"][persp] = mean(
                merged_group_size_hist[act][persp])
        # max
        agg_merged_group_size_hist[act]["max"] = dict()
        for persp in merged_group_size_hist[act].keys():
            agg_merged_group_size_hist[act]["max"][persp] = mean(
                merged_group_size_hist[act][persp])

        # min
        agg_merged_group_size_hist[act]["min"] = dict()
        for persp in merged_group_size_hist[act].keys():
            agg_merged_group_size_hist[act]["min"][persp] = mean(
                merged_group_size_hist[act][persp])

    return agg_merged_group_size_hist
