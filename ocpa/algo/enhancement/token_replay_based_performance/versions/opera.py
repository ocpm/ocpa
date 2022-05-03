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
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.statistics.variants.log import get as variants_module
from pm4py.visualization.petrinet.util import performance_map
from ocpa.algo.enhancement.token_replay_based_performance.util import run_timed_replay
from ocpa.objects.log.importer.mdl.util import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.algo.discovery.mvp.projection import algorithm as projection_factory
run_timed_replay


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

    # def __hash__(self):
    #     return hash(tuple([self.transition.label, self.event]))

    def __eq__(self, eo):
        return self.transition.name == eo.transition.name and self.event == eo.event


class PerformanceAnalysis:
    def __init__(self, object_map):
        self.perf_records = {}
        self.object_map = object_map

    def correspond(self, eo: EventOccurrence, V: Set[TokenVisit]):
        input_places = [
            in_arc.source for in_arc in eo.transition.in_arcs]
        return [v for v in V if v.end == eo.event[ocpa_constants.DEFAULT_OCEL_START_TIMESTAMP_KEY] and v.token[0].name in [p.name for p in input_places]]

    def analyze(self, eos: Set[EventOccurrence], tvs: Set[TokenVisit], ots: Set[str], parameters):
        # compute measures
        if 'waiting_time' in parameters['measures']:
            p_waiting = True
        else:
            p_waiting = False
        if 'service_time' in parameters['measures']:
            p_service = True
        else:
            p_service = False
        if 'sojourn_time' in parameters['measures']:
            p_sojourn = True
        else:
            p_sojourn = False
        if 'synchronization_time' in parameters['measures']:
            p_sync = True
        else:
            p_sync = False
        if 'pooling_time' in parameters['measures']:
            p_pooling = True
        else:
            p_pooling = False
        if 'lagging_time' in parameters['measures']:
            p_lagging = True
        else:
            p_lagging = False

        if 'flow_time' in parameters['measures']:
            p_flow = True
        else:
            p_flow = False

        if p_waiting:
            self.perf_records['waiting'] = {}
        if p_service:
            self.perf_records['service'] = {}
        if p_sojourn:
            self.perf_records['sojourn'] = {}
        if p_sync:
            self.perf_records['synchronization'] = {}
        if p_pooling:
            self.perf_records['pooling'] = {}
            for ot in ots:
                self.perf_records['pooling'][ot] = {}
        if p_lagging:
            self.perf_records['lagging'] = {}
            for ot in ots:
                self.perf_records['lagging'][ot] = {}
        if p_flow:
            self.perf_records['flow'] = {}
        eos_len = len(eos)
        i = 0
        for eo in eos:
            i += 1
            if i % 1000 == 0:
                print(f'{i}/{eos_len}')
            R = self.correspond(eo, tvs)
            # if len(R) > 1:
            #     print(f'Event occurence: {eo}')
            #     print(f'Token visits: {tvs}')
            #     print(f'Corresponding: {R}')
            if p_waiting:
                waiting = self.measure_waiting(eo, R)
                if eo.transition.name in self.perf_records['waiting']:
                    self.perf_records['waiting'][eo.transition.name].append(
                        waiting)
                else:
                    self.perf_records['waiting'][eo.transition.name] = [
                        waiting]
            if p_service:
                service = self.measure_service(eo, R)
                if eo.transition.name in self.perf_records['service']:
                    self.perf_records['service'][eo.transition.name].append(
                        service)
                else:
                    self.perf_records['service'][eo.transition.name] = [
                        service]
            if p_sojourn:
                if p_waiting is True and p_service is not True:
                    service = self.measure_service(eo, R)
                    sojourn = waiting + service
                elif p_waiting is not True and p_service is True:
                    waiting = self.measure_waiting(eo, R)
                    sojourn = waiting + service
                else:
                    sojourn = self.measure_sojourn(eo, R)

                if eo.transition.name in self.perf_records['sojourn']:
                    self.perf_records['sojourn'][eo.transition.name].append(
                        sojourn)
                else:
                    self.perf_records['sojourn'][eo.transition.name] = [
                        sojourn]
            if p_sync:
                sync = self.measure_synchronization(eo, R)
                if eo.transition.name in self.perf_records['synchronization']:
                    self.perf_records['synchronization'][eo.transition.name].append(
                        sync)
                else:
                    self.perf_records['synchronization'][eo.transition.name] = [
                        sync]
            if p_pooling:
                for ot in ots:
                    ot_pooling = self.measure_pooling(eo, R, ot)
                    if eo.transition.name in self.perf_records['pooling'][ot]:
                        self.perf_records['pooling'][ot][eo.transition.name].append(
                            ot_pooling)
                    else:
                        self.perf_records['pooling'][ot][eo.transition.name] = [
                            ot_pooling]
            if p_lagging:
                for ot in ots:
                    ot_lagging = self.measure_lagging(eo, R, ot)
                    if eo.transition.name in self.perf_records['lagging'][ot]:
                        self.perf_records['lagging'][ot][eo.transition.name].append(
                            ot_lagging)
                    else:
                        self.perf_records['lagging'][ot][eo.transition.name] = [
                            ot_lagging]
            if p_flow:
                if p_sojourn is not True and p_sync is True:
                    if p_waiting is True and p_service is not True:
                        service = self.measure_service(eo, R)
                        sojourn = waiting + service
                    elif p_waiting is not True and p_service is True:
                        waiting = self.measure_waiting(eo, R)
                        sojourn = waiting + service
                    else:
                        sojourn = self.measure_sojourn(eo, R)
                elif p_sojourn is True and p_sync is not True:
                    sync = self.measure_synchronization(eo, R)
                else:
                    sojourn = self.measure_sojourn(eo, R)
                    sync = self.measure_synchronization(eo, R)
                flow = sojourn + sync
                if eo.transition.name in self.perf_records['flow']:
                    self.perf_records['flow'][eo.transition.name].append(
                        flow)
                else:
                    self.perf_records['flow'][eo.transition.name] = [
                        flow]

        # aggregate measures
        perf_diag = {}
        if p_waiting:
            perf_diag['agg_waiting_time'] = aggregate_perf_records(
                self.perf_records, measure_name='waiting', aggregation_measure='all')
        if p_service:
            perf_diag['agg_service_time'] = aggregate_perf_records(
                self.perf_records, measure_name='service', aggregation_measure='all')
        if p_sojourn:
            perf_diag['agg_sojourn_time'] = aggregate_perf_records(
                self.perf_records, measure_name='sojourn', aggregation_measure='all')
        if p_sync:
            perf_diag['agg_synchronization_time'] = aggregate_perf_records(
                self.perf_records, measure_name='synchronization', aggregation_measure='all')

        if p_pooling:
            perf_diag['agg_pooling_time'] = {}
            for persp in ots:
                perf_diag['agg_pooling_time'][persp] = aggregate_perf_records(
                    self.perf_records, measure_name='pooling', aggregation_measure='all', ot=persp)

        if p_lagging:
            perf_diag['agg_lagging_time'] = {}
            for persp in ots:
                perf_diag['agg_lagging_time'][persp] = aggregate_perf_records(
                    self.perf_records, measure_name='lagging', aggregation_measure='all', ot=persp)
        if p_flow:
            perf_diag['agg_flow_time'] = aggregate_perf_records(
                self.perf_records, measure_name='flow', aggregation_measure='all')
        return perf_diag

    def measure_waiting(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            waiting = (
                eo.event[ocpa_constants.DEFAULT_OCEL_START_TIMESTAMP_KEY] - min(start_times)).total_seconds()
            if waiting < 0:
                return 0
            return waiting
        else:
            return 0

    def measure_service(self, eo: EventOccurrence, R: Set[TokenVisit]):
        service = (
            eo.event[ocpa_constants.DEFAULT_OCEL_TIMESTAMP_KEY] - eo.event[ocpa_constants.DEFAULT_OCEL_START_TIMESTAMP_KEY]).total_seconds()
        if service < 0:
            return 0
        return service

    def measure_sojourn(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            sojourn = (
                eo.event[ocpa_constants.DEFAULT_OCEL_TIMESTAMP_KEY] - min(start_times)).total_seconds()
            if sojourn < 0:
                return 0
            return sojourn
        else:
            return 0

    def measure_synchronization(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            sync = (max(start_times) - min(start_times)).total_seconds()
            if sync < 0:
                return 0
            return sync
        else:
            return 0

    def measure_pooling(self, eo: EventOccurrence, R: Set[TokenVisit], ot: str):
        ot_R = [r for r in R if r.token[1] in self.object_map[ot]]
        if len(ot_R) > 0:
            ot_start_times = [
                r.start for r in ot_R]
            pooling = (max(ot_start_times) -
                       min(ot_start_times)).total_seconds()
            if pooling < 0:
                return 0
            return pooling
        else:
            return 0

    def measure_lagging(self, eo: EventOccurrence, R: Set[TokenVisit], ot: str):
        ot_R = [r for r in R if r.token[1] in self.object_map[ot]]
        if len(ot_R) > 0:
            start_times = [r.start for r in R]
            ot_start_times = [
                r.start for r in ot_R]
            lagging = (max(ot_start_times) - min(start_times)).total_seconds()
            if lagging < 0:
                return 0
            return lagging
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


def aggregate_ot_stats(perf_records, measure_name, ot, elem, aggregation_measure):
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
        if ot in perf_records[measure_name]:
            aggr_stat = mean(perf_records[measure_name][ot][elem])
    elif aggregation_measure == "median":
        if ot in perf_records[measure_name]:
            aggr_stat = median(perf_records[measure_name][ot][elem])
    elif aggregation_measure == "stdev":
        if ot in perf_records[measure_name]:
            if len(perf_records[measure_name][ot][elem]) > 1:
                aggr_stat = stdev(perf_records[measure_name][ot][elem])
        else:
            aggr_stat = 0
    elif aggregation_measure == "sum":
        if ot in perf_records[measure_name]:
            aggr_stat = sum(perf_records[measure_name][ot][elem])
    elif aggregation_measure == "min":
        if ot in perf_records[measure_name]:
            aggr_stat = min(perf_records[measure_name][ot][elem])
    elif aggregation_measure == "max":
        if ot in perf_records[measure_name]:
            aggr_stat = max(perf_records[measure_name][ot][elem])
    aggr_stat = human_readable_stat(aggr_stat)
    return aggr_stat


def aggregate_perf_records(perf_records, measure_name="waiting", aggregation_measure='all', ot=None):
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
    if ot is not None:
        if ot in perf_records[measure_name]:
            for elem in perf_records[measure_name][ot].keys():
                if aggregation_measure == 'all':
                    for agg in ['mean', 'median', 'min', 'max', 'stdev']:
                        aggr_stat = aggregate_ot_stats(
                            perf_records, measure_name, ot, elem, agg)
                        if elem not in aggregated_perf_records:
                            aggregated_perf_records[elem] = {}
                        aggregated_perf_records[elem][agg] = aggr_stat
                else:
                    aggr_stat = aggregate_ot_stats(
                        perf_records, measure_name, ot, elem, agg)
                    if elem not in aggregated_perf_records:
                        aggregated_perf_records[elem] = {}
                    aggregated_perf_records[elem][agg] = aggr_stat
    else:

        for elem in perf_records[measure_name].keys():
            if aggregation_measure == 'all':
                for agg in ['mean', 'median', 'min', 'max', 'stdev']:
                    aggr_stat = aggregate_stats(
                        perf_records, measure_name, elem, agg)
                    if elem not in aggregated_perf_records:
                        aggregated_perf_records[elem] = {}
                    aggregated_perf_records[elem][agg] = aggr_stat
            else:
                aggr_stat = aggregate_stats(
                    perf_records, measure_name, elem, aggregation_measure)
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

    if 'measures' not in parameters:
        parameters['measures'] = ['sojourn time']

    if 'agg' not in parameters:
        parameters['agg'] = ['mean']

    allowed_activities = parameters["allowed_activities"] if "allowed_activities" in parameters else None
    debug = parameters["debug"] if "debug" in parameters else False

    eos = []

    for i, row in df.iterrows():
        act = row['event_activity']
        start_timestamp = row['event_start_timestamp']
        timestamp = row['event_timestamp']
        event = {'event_activity': act,
                 'event_start_timestamp': start_timestamp, 'event_timestamp': timestamp}
        trans = ocpn.find_transition(act)
        eo = EventOccurrence(trans, event)
        eos.append(eo)

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

    diff_log = 0
    diff_model = 0
    diff_token_replay = 0
    diff_performance_annotation = 0
    diff_basic_stats = 0

    persps = ocpn.object_types
    object_map = {}

    replay_diag = dict()
    replay_diag["act_freq"] = {}
    replay_diag["arc_freq_persps"] = {}
    replay_diag["group_size_hist"] = {}
    replay_diag["place_fitness_per_trace"] = {}

    for persp in persps:
        net, im, fm = ocpn.nets[persp]
        object_map[persp] = set(df[persp])
        # remove nan
        object_map[persp] = {x for x in object_map[persp] if x == x}
        log = projection_factory.apply(df, persp, parameters=parameters)

        if allowed_activities is not None:
            if persp not in allowed_activities:
                continue
            filtered_log = attributes_filter.apply_events(
                log, allowed_activities[persp])
        else:
            filtered_log = log

        # Diagonstics - Activity Counting
        activ_count = projection_factory.apply(
            df, persp, variant="activity_occurrence", parameters=parameters)
        replay_diag["act_freq"][persp] = activ_count

        variants_idx = variants_module.get_variants_from_log_trace_idx(log)

        aligned_traces, place_fitness_per_trace, transition_fitness_per_trace, notexisting_activities_in_model = run_timed_replay(
            log, net, im, fm, parameters={"enable_pltr_fitness": True, "disable_variants": True})
        replay_diag["place_fitness_per_trace"][persp] = place_fitness_per_trace

        token_visits = [y for x in aligned_traces for y in x['token_visits']]
        event_occurrences = [
            y for trace in aligned_traces for y in trace['event_occurrences']]

        for tv in token_visits:
            tvs.append(TokenVisit(tv[0], tv[1], tv[2]))
        # for eo in event_occurrences:
        #     eos.append(EventOccurrence(eo[0], eo[1]))

        element_statistics = performance_map.single_element_statistics(
            log, net, im, aligned_traces, variants_idx)

        agg_statistics = aggregate_frequencies(element_statistics)
        replay_diag["arc_freq_persps"][persp] = agg_statistics

        if 'group_size' in parameters['measures']:
            group_size_hist = projection_factory.apply(
                df, persp, variant="group_size_hist", parameters=parameters)
            replay_diag["group_size_hist"][persp] = group_size_hist

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

    replay_diag["act_freq"] = merge_act_freq(replay_diag["act_freq"])
    replay_diag["arc_freq"] = merge_replay(ocpn,
                                           replay_diag["arc_freq_persps"])
    merged_group_size_hist = merge_group_size_hist(
        replay_diag["group_size_hist"])
    replay_diag["group_size_hist"] = agg_merged_group_size_hist(
        merged_group_size_hist)
    replay_diag["place_fitness_per_trace"] = merge_place_fitness(
        replay_diag["place_fitness_per_trace"])

    tvs = list(set(tvs))
    # eos = list(set(eos))
    pa = PerformanceAnalysis(object_map)
    perf_diag = pa.analyze(eos, tvs, persps, parameters)

    # merge replay diagnostics and performance diagnostics
    diag = {**perf_diag, **replay_diag}
    transformed_diag = transform_diagnostics(ocpn, diag, parameters)

    return transformed_diag


def transform_diagnostics(ocpn, diag, parameters):

    if 'waiting_time' in parameters['measures']:
        p_waiting = True
    else:
        p_waiting = False
    if 'service_time' in parameters['measures']:
        p_service = True
    else:
        p_service = False
    if 'sojourn_time' in parameters['measures']:
        p_sojourn = True
    else:
        p_sojourn = False
    if 'synchronization_time' in parameters['measures']:
        p_sync = True
    else:
        p_sync = False
    if 'pooling_time' in parameters['measures']:
        p_pooling = True
    else:
        p_pooling = False
    if 'lagging_time' in parameters['measures']:
        p_lagging = True
    else:
        p_lagging = False
    if 'group_size' in parameters['measures']:
        p_group_size = True
    else:
        p_group_size = False
    if 'act_freq' in parameters['measures']:
        p_act_freq = True
    else:
        p_act_freq = False
    if 'arc_freq' in parameters['measures']:
        p_arc_freq = True
    else:
        p_arc_freq = False
    if 'flow_time' in parameters['measures']:
        p_flow = True
    else:
        p_flow = False

    transformed_diag = {}

    for tr in ocpn.transitions:
        if tr.silent == False:
            transformed_diag[tr.name] = {}
            # transformed_diag[tr.name]["act_freq"] = textualize_act_freq(
            #     tr.name, diag['act_freq'])
            transformed_diag[tr.name]["act_freq"] = diag['act_freq'][tr.name]

            if p_group_size:
                transformed_diag[tr.name]["group_size_hist"] = textualize_group_size(
                    tr.name, parameters['agg'], diag["group_size_hist"])

            if p_waiting:
                transformed_diag[tr.name]['waiting_time'] = textualize_waiting_time(
                    tr.name, parameters['agg'], diag['agg_waiting_time'])

            if p_service:
                transformed_diag[tr.name]['service_time'] = textualize_service_time(
                    tr.name, parameters['agg'], diag['agg_service_time'])

            if p_sojourn:
                transformed_diag[tr.name]['sojourn_time'] = textualize_sojourn_time(
                    tr.name, parameters['agg'], diag['agg_sojourn_time'])

            if p_sync:
                transformed_diag[tr.name]['synchronization_time'] = textualize_synchronization_time(
                    tr.name, parameters['agg'], diag['agg_synchronization_time'])

            if p_pooling:
                transformed_diag[tr.name]['pooling_time'] = textualize_pooling_time(
                    tr.name, ocpn.object_types, parameters['agg'], diag['agg_pooling_time'])

            if p_lagging:
                transformed_diag[tr.name]['lagging_time'] = textualize_lagging_time(
                    tr.name, ocpn.object_types, parameters['agg'], diag['agg_lagging_time'])

            if p_flow:
                transformed_diag[tr.name]['flow_time'] = textualize_flow_time(
                    tr.name, parameters['agg'], diag['agg_flow_time'])

    transformed_diag['arc_freq'] = diag['arc_freq']

    return transformed_diag


# def merge_agg_performance(agg_performance):
#     merged_agg_performance = dict()
#     for persp in agg_performance:
#         for el in agg_performance[persp]:
#             merged_agg_performance[repr(el)] = agg_performance[persp][el]
#     return merged_agg_performance


def merge_replay(ocpn, replay):
    merged_replay = dict()
    arcs = [a for a in ocpn.arcs]
    for persp in replay.keys():
        for elem in replay[persp].keys():
            if type(elem) is PetriNet.Arc:
                arc_name = ""
                if type(elem.source) == PetriNet.Place:
                    arc_name += "(p)" + elem.source.name
                else:
                    if elem.source.label:
                        arc_name += "(t)" + elem.source.label
                    else:
                        arc_name += "(t)" + elem.source.name
                arc_name += "->"
                if type(elem.target) == PetriNet.Place:
                    arc_name += "(p)" + elem.target.name
                else:
                    if elem.target.label:
                        arc_name += "(t)" + elem.target.label
                    else:
                        arc_name += "(t)" + elem.target.name

                merged_replay[arc_name] = replay[persp][elem]
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


def textualize_act_freq(tr_name, act_freq):
    text = "Activity frequency: "
    text += f'{act_freq[tr_name]}'
    return text


def textualize_waiting_time(tr_name, aggs, waiting_time):
    record = {}
    text = "Waiting time: {"
    for agg in aggs:
        text += f' {agg}: '
        if agg in waiting_time[tr_name]:
            record[agg] = waiting_time[tr_name][agg]
            text += f'{waiting_time[tr_name][agg]}'
    text += '}'
    return record


def textualize_service_time(tr_name, aggs, service_time):
    record = {}
    text = "Service time: {"
    for agg in aggs:
        text += f' {agg}: '
        if agg in service_time[tr_name]:
            record[agg] = service_time[tr_name][agg]
            text += f'{service_time[tr_name][agg]}'
    text += '}'
    return record


def textualize_sojourn_time(tr_name, aggs, sojourn_time):
    record = {}
    text = "sojourn time: {"
    for agg in aggs:
        text += f' {agg}: '
        if agg in sojourn_time[tr_name]:
            record[agg] = sojourn_time[tr_name][agg]
            text += f'{sojourn_time[tr_name][agg]}'
    text += '}'
    return record


def textualize_synchronization_time(tr_name, aggs, synchronization_time):
    record = {}
    text = "synchronization time: {"
    for agg in aggs:
        text += f' {agg}: '
        if agg in synchronization_time[tr_name]:
            record[agg] = synchronization_time[tr_name][agg]
            text += f'{synchronization_time[tr_name][agg]}'
    text += '}'
    return record


def textualize_group_size(tr_name, aggs, group_size):
    record = {}
    text = "Number of objects: { "
    for agg in aggs:
        text += f'{agg}: {{'
        record[agg] = {}
        if agg in group_size[tr_name]:
            for obj_type in group_size[tr_name][agg].keys():
                record[agg][obj_type] = group_size[tr_name][agg][obj_type]
                text += f" {obj_type}={group_size[tr_name][agg][obj_type]} "
        text += '} '
    text += '}'
    return record


def textualize_lagging_time(tr_name, obj_types, aggs, lagging_time):
    record = {}
    text = "lagging time: { "
    for obj_type in obj_types:
        record[obj_type] = {}
        if tr_name in lagging_time[obj_type]:
            text += f'{obj_type}: {{'
            for agg in aggs:
                if agg in lagging_time[obj_type][tr_name]:
                    record[obj_type][agg] = lagging_time[obj_type][tr_name][agg]
                    text += f'{agg}: {{'
                    text += f" {obj_type}={lagging_time[obj_type][tr_name][agg]} "
                    text += '} '
            text += '} '
    text += '}'
    return record


def textualize_pooling_time(tr_name, obj_types, aggs, pooling_time):
    record = {}
    text = "Pooling time: { "
    for obj_type in obj_types:
        record[obj_type] = {}
        if tr_name in pooling_time[obj_type]:
            text += f'{obj_type}: {{'
            for agg in aggs:
                if agg in pooling_time[obj_type][tr_name]:
                    record[obj_type][agg] = pooling_time[obj_type][tr_name][agg]
                    text += f'{agg}: {{'
                    text += f" {obj_type}={pooling_time[obj_type][tr_name][agg]} "
                    text += '} '
            text += '} '
    text += '}'

    return record


def textualize_flow_time(tr_name, aggs, flow_time):
    record = {}
    text = "flow time: {"
    for agg in aggs:
        text += f' {agg}: '
        if agg in flow_time[tr_name]:
            record[agg] = flow_time[tr_name][agg]
            text += f'{flow_time[tr_name][agg]}'
    text += '}'
    return record
