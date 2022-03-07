from typing import List, Dict, Set, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from ocpa.util.vis_util import human_readable_stat
from statistics import median, mean
from ocpa.util import constants as ocpa_constants
import time
import pandas as pd
from statistics import stdev
import uuid
from copy import deepcopy
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from pm4py.objects.petri.utils import remove_place, remove_transition
from pm4py.objects.petri.utils import add_arc_from_to
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.statistics.variants.log import get as variants_module
from pm4py.visualization.petrinet.util import performance_map
from ocpa.algo.enhancement.token_replay_based_performance.util import run_timed_replay
from pm4py.objects.conversion.dfg import converter as dfg_converter
from pm4py.statistics.end_activities.log import get as ea_get
from pm4py.statistics.start_activities.log import get as sa_get
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
import pm4py
# from pm4pymdl.algo.mvp.utils import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.objects.log.importer.mdl.util import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.algo.discovery.mvp.projection import algorithm as projection_factory
run_timed_replay
# from pm4py.algo.conformance.tokenreplay import algorithm as tr_factory

PARAM_ACTIVITY_KEY = pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY
MAX_FREQUENCY = float("inf")


@dataclass
class TokenVisit:
    token: Tuple[str, str]
    start: Any
    end: Any

    def __hash__(self):
        return hash(tuple([self.token, self.start, self.end]))


@dataclass
class EventOccurrence:
    transition: Any
    event: Any

    def __hash__(self):
        return hash(tuple([self.transition.label, self.event]))

    def __eq__(self, eo):
        return self.transition.label == eo.transition.label and self.event == eo.event


class PerformanceAnalysis:
    def __init__(self):
        self.perf_records = {}

    def correspond(self, eo: EventOccurrence, V: Set[TokenVisit]):
        return [v for v in V if v.end == eo.event[ocpa_constants.DEFAULT_START_TIMESTAMP_KEY]]

    def analyze(self, eos: Set[EventOccurrence], tvs: Set[TokenVisit]):
        self.perf_records['waiting'] = {}
        self.perf_records['service'] = {}
        self.perf_records['sojourn'] = {}
        self.perf_records['synchronization'] = {}
        eos_len = len(eos)
        i = 0
        for eo in eos:
            i += 1
            if i % 1000 == 0:
                print(f'{i}/{eos_len}')
            R = self.correspond(eo, tvs)
            waiting = self.measure_waiting(eo, R)
            service = self.measure_service(eo, R)
            sojourn = waiting + service
            sync = self.measure_synchronization(eo, R)
            if eo.transition.label in self.perf_records['waiting']:
                self.perf_records['waiting'][eo.transition.label].append(
                    waiting)
            else:
                self.perf_records['waiting'][eo.transition.label] = [waiting]

            if eo.transition.label in self.perf_records['service']:
                self.perf_records['service'][eo.transition.label].append(
                    service)
            else:
                self.perf_records['service'][eo.transition.label] = [service]

            if eo.transition.label in self.perf_records['sojourn']:
                self.perf_records['sojourn'][eo.transition.label].append(
                    sojourn)
            else:
                self.perf_records['sojourn'][eo.transition.label] = [sojourn]

            if eo.transition.label in self.perf_records['synchronization']:
                self.perf_records['synchronization'][eo.transition.label].append(
                    sync)
            else:
                self.perf_records['synchronization'][eo.transition.label] = [
                    sync]

        return self.perf_records

    def measure_waiting(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            waiting = (
                eo.event[ocpa_constants.DEFAULT_START_TIMESTAMP_KEY] - min(start_times)).total_seconds()
            return waiting
        else:
            return 0

    def measure_service(self, eo: EventOccurrence, R: Set[TokenVisit]):
        service = (
            eo.event[ocpa_constants.DEFAULT_TIMESTAMP_KEY] - eo.event[ocpa_constants.DEFAULT_START_TIMESTAMP_KEY]).total_seconds()
        return service

    def measure_synchronization(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            sync = (max(start_times) - min(start_times)).total_seconds()
            return sync
        else:
            return 0


def aggregate_stats(perf_records, measure_name, elem, aggregation_measure):
    """
    Aggregate the perf_records

    Parameters
    -----------
    perf_records
        Element perf_records
    elem
        Current element
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use

    Returns
    -----------
    aggr_stat
        Aggregated perf_records
    """
    aggr_stat = 0
    if aggregation_measure == "mean" or aggregation_measure is None:
        aggr_stat = mean(perf_records[measure_name][elem])
    elif aggregation_measure == "median":
        aggr_stat = median(perf_records[measure_name][elem])
    elif aggregation_measure == "stdev":
        if len(perf_records[measure_name][elem]) > 1:
            aggr_stat = stdev(perf_records[measure_name][elem])
        else:
            aggr_stat = 0
    elif aggregation_measure == "sum":
        aggr_stat = sum(perf_records[measure_name][elem])
    elif aggregation_measure == "min":
        aggr_stat = min(perf_records[measure_name][elem])
    elif aggregation_measure == "max":
        aggr_stat = max(perf_records[measure_name][elem])
    aggr_stat = human_readable_stat(aggr_stat)
    return aggr_stat


def aggregate_perf_records(perf_records, measure_name="waiting", aggregation_measure='all'):
    """
    Gets aggregated perf_records

    Parameters
    ----------
    perf_records
        Individual element perf_records (including unaggregated performances)
    measure
        Desidered view on data (frequency or performance)
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use

    Returns
    ----------
    aggregated_perf_records
        Aggregated perf_records for arcs, transitions, places
    """
    aggregated_perf_records = {}
    for elem in perf_records[measure_name].keys():
        if aggregation_measure == 'all':
            for agg in ['mean', 'median', 'min', 'max', 'stdev']:
                aggr_stat = aggregate_stats(
                    perf_records, measure_name, elem, agg)
        # aggr_stat_hr = human_readable_stat(aggr_stat)
                if elem not in aggregated_perf_records:
                    aggregated_perf_records[elem] = {}
                aggregated_perf_records[elem][agg] = aggr_stat
        else:
            aggr_stat = aggregate_stats(
                perf_records, measure_name, elem, aggregation_measure)
            # aggr_stat_hr = human_readable_stat(aggr_stat)
            if elem not in aggregated_perf_records:
                aggregated_perf_records[elem] = {}
            aggregated_perf_records[elem][aggregation_measure] = aggr_stat
    return aggregated_perf_records


def aggregate_frequencies(statistics):
    """
    Gets aggregated statistics

    Parameters
    ----------
    statistics
        Individual element statistics (including unaggregated performances)

    Returns
    ----------
    aggregated_statistics
        Aggregated statistics for arcs, transitions, places
    """
    aggregated_statistics = {}
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            freq = statistics[elem]["count"]
            aggregated_statistics[elem] = str(freq)
        elif type(elem) is PetriNet.Transition:
            if elem.label is not None:
                freq = statistics[elem]["count"]
                aggregated_statistics[elem] = elem.label + \
                    " (" + str(freq) + ")"
        elif type(elem) is PetriNet.Place:
            pass
    return aggregated_statistics


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

    tvs = []
    eos = []

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
    # # when replaying streaming log, some objects are missing.
    # persps = [x for x in persps if x in df.columns]

    for persp in persps:
        net, im, fm = ocpn.nets[persp]
        aa = time.time()

        log = projection_factory.apply(df, persp, parameters=parameters)

        if allowed_activities is not None:
            if persp not in allowed_activities:
                continue
            filtered_log = attributes_filter.apply_events(
                log, allowed_activities[persp])
        else:
            filtered_log = log
        bb = time.time()
        diff_log += (bb - aa)

        cc = time.time()

        dd = time.time()

        diff_model += (dd - cc)

        # Diagonstics - Activity Counting
        xx1 = time.time()
        activ_count = projection_factory.apply(
            df, persp, variant="activity_occurrence", parameters=parameters)

        xx2 = time.time()

        ee = time.time()
        variants_idx = variants_module.get_variants_from_log_trace_idx(log)
        # variants = variants_module.convert_variants_trace_idx_to_trace_obj(log, variants_idx)
        # parameters_tr = {PARAM_ACTIVITY_KEY: "concept:name", "variants": variants}

        aligned_traces, place_fitness_per_trace, transition_fitness_per_trace, notexisting_activities_in_model = run_timed_replay(
            log, net, im, fm, parameters={"enable_pltr_fitness": True, "disable_variants": True})

        token_visits = [y for x in aligned_traces for y in x['token_visits']]
        event_occurrences = [
            y for x in aligned_traces for y in x['event_occurrences']]

        for tv in token_visits:
            tvs.append(TokenVisit(tv[0], tv[1], tv[2]))
        for eo in event_occurrences:
            eos.append(EventOccurrence(eo[0], eo[1]))

        element_statistics = performance_map.single_element_statistics(
            log, net, im, aligned_traces, variants_idx)

        agg_statistics = aggregate_frequencies(
            element_statistics)
        # agg_performance_min = aggregate_statistics(
        #     element_statistics, measure="performance", aggregation_measure="min")
        # agg_performance_max = aggregate_statistics(
        #     element_statistics, measure="performance", aggregation_measure="max")
        # agg_performance_median = aggregate_statistics(
        #     element_statistics, measure="performance", aggregation_measure="median")
        # agg_performance_mean = aggregate_statistics(
        #     element_statistics, measure="performance", aggregation_measure="mean")

        group_size_hist = projection_factory.apply(
            df, persp, variant="group_size_hist", parameters=parameters)

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

        # Diagnostics on transitions
        diag["act_freq"][persp] = activ_count
        diag["arc_freq"][persp] = agg_statistics
        # diag["aligned_traces"][persp] = aligned_traces
        diag["place_fitness_per_trace"][persp] = place_fitness_per_trace
        diag["agg_statistics_frequency"][persp] = agg_statistics
        # diag["agg_performance_min"][persp] = agg_performance_min
        # diag["agg_performance_max"][persp] = agg_performance_max
        # diag["agg_performance_median"][persp] = agg_performance_median
        # diag["agg_performance_mean"][persp] = agg_performance_mean
        diag["group_size_hist"][persp] = group_size_hist
        # diag["act_freq_replay"][persp] = len_different_ids
        # diag["group_size_hist_replay"][persp] = eid_acti_count

    tvs = list(set(tvs))
    eos = list(set(eos))
    pa = PerformanceAnalysis()
    perf_records = pa.analyze(eos, tvs)
    # for eo in eos:
    #     perf_records['']
    #     if eo.transition.label == 'Cancel application':
    #         R = pa.correspond(eo, tvs)
    #         print(f'Event: {eo}')
    #         print(f'Corresponding Tokens: {R}')
    #         print(f'Waiting Time: {pa.measure_waiting(eo, R)}')

    # with open("replay-{}.txt".format(persp), "w") as text_file:
    #     text_file.write(str(tvs))
    diag['agg_waiting_time'] = aggregate_perf_records(perf_records,
                                                      measure_name='waiting', aggregation_measure='all')
    diag['agg_service_time'] = aggregate_perf_records(perf_records,
                                                      measure_name='service', aggregation_measure='all')
    diag['agg_sojourn_time'] = aggregate_perf_records(perf_records,
                                                      measure_name='sojourn', aggregation_measure='all')
    diag['agg_synchronization_time'] = aggregate_perf_records(perf_records,
                                                              measure_name='synchronization', aggregation_measure='all')

    # diag["computation_statistics"] = {"diff_log": diff_log, "diff_model": diff_model,
    #                                   "diff_token_replay": diff_token_replay,
    #                                   "diff_performance_annotation": diff_performance_annotation,
    #                                   "diff_basic_stats": diff_basic_stats}

    # Transitions
    diag["replayed_act_freq"] = merge_act_freq(diag["act_freq"])
    diag["replayed_arc_frequency"] = merge_replay(diag["arc_freq"])
    merged_group_size_hist = merge_group_size_hist(diag["group_size_hist"])
    diag["agg_merged_group_size_hist"] = agg_merged_group_size_hist(
        merged_group_size_hist)
    diag["replayed_place_fitness"] = merge_place_fitness(
        diag["place_fitness_per_trace"])
    # diag["replayed_performance_median"] = merge_agg_performance(
    #     diag["agg_performance_median"])
    # diag["replayed_performance_mean"] = merge_agg_performance(
    #     diag["agg_performance_mean"])
    # diag["replayed_performance_min"] = merge_agg_performance(
    #     diag["agg_performance_min"])
    # diag["replayed_performance_max"] = merge_agg_performance(
    #     diag["agg_performance_max"])

    # Places

    print(diag)
    return diag


# def merge_agg_performance(agg_performance):
#     merged_agg_performance = dict()
#     for persp in agg_performance:
#         for el in agg_performance[persp]:
#             merged_agg_performance[repr(el)] = agg_performance[persp][el]
#     return merged_agg_performance


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
