from operator import attrgetter
from typing import Set, Any, Tuple
from dataclasses import dataclass
from statistics import median, mean
from ocpa.util import constants as ocpa_constants
import pandas as pd
from statistics import stdev
from pm4py.objects.petri_net.obj import PetriNet
from ocpa.algo.enhancement.token_replay_based_performance.util import run_timed_replay, single_element_statistics
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl, clean_frequency, clean_arc_frequency
from ocpa.algo.util.util import project_log


def apply(ocpn, ocel, parameters=None):
    if parameters is None:
        parameters = {}

    if 'measures' not in parameters:
        parameters['measures'] = ['sojourn time']

    if 'agg' not in parameters:
        parameters['agg'] = ['mean']

    persps = ocpn.object_types

    replay_diag = dict()
    replay_diag["act_freq"] = {}
    replay_diag["arc_freq_persps"] = {}
    replay_diag["object_count"] = {}
    replay_diag["place_fitness_per_trace"] = {}

    debug = parameters["debug"] if "debug" in parameters else False

    eos = []
    df = ocel.log.log

    for ei in ocel.obj.raw.events:
        event = ocel.obj.raw.events[ei]
        trans = ocpn.find_transition(event.act)
        eo = EventOccurrence(trans, event)
        eos.append(eo)

    for persp in persps:
        replay_diag["object_count"][persp] = dict()

    act_names = set(df['event_activity'])
    acts = list(df['event_activity'])
    for act_name in act_names:
        replay_diag["act_freq"][act_name] = acts.count(act_name)

    for i, row in df.iterrows():
        act = row['event_activity']

        for persp in persps:
            if row[persp] is not float and len(row[persp]) > 0:
                if act in replay_diag["object_count"][persp]:
                    replay_diag["object_count"][persp][act].append(
                        len(row[persp]))
                else:
                    replay_diag["object_count"][persp][act] = [
                        len(row[persp])]

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
    object_map = {}

    for persp in persps:
        net, im, fm = ocpn.nets[persp]
        object_map[persp] = set(df[persp])
        # remove nan
        object_map[persp] = {x for x in object_map[persp] if x == x}
        log = project_log(df, persp, parameters=parameters)

        replay_results = run_timed_replay(log, net, im, fm)

        token_visits = [y for x in replay_results for y in x['token_visits']]

        for tv in token_visits:
            tvs.append(TokenVisit(tv[0], tv[1], tv[2]))

        element_statistics = single_element_statistics(
            log, net, im, replay_results)

        agg_statistics = aggregate_frequencies(element_statistics)
        replay_diag["arc_freq_persps"][persp] = agg_statistics

    replay_diag["arc_freq"] = merge_replay(ocpn,
                                           replay_diag["arc_freq_persps"])
    replay_diag['agg_object_freq'] = {}
    for persp in persps:
        replay_diag['agg_object_freq'][persp] = aggregate_perf_records(
            replay_diag['object_count'], aggregation_measure='all', ot=persp)
    # replay_diag['agg_object_freq'] = replay_diag['object_count']
    replay_diag["place_fitness_per_trace"] = merge_place_fitness(
        replay_diag["place_fitness_per_trace"])
    replay_diag["object_count"] = replay_diag['agg_object_freq']

    tvs = list(set(tvs))
    pa = PerformanceAnalysis(object_map, ocpn.place_mapping)
    perf_diag = pa.analyze(eos, tvs, persps, parameters)

    # merge replay diagnostics and performance diagnostics
    diag = {**perf_diag, **replay_diag}
    transformed_diag = transform_diagnostics(ocpn, diag, parameters)

    return transformed_diag


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
        return self.transition.label == eo.transition.label and self.event == eo.event


class PerformanceAnalysis:
    def __init__(self, object_map, place_mapping):
        self.perf_records = {}
        self.object_map = object_map
        self.place_mapping = place_mapping

    def correspond(self, eo: EventOccurrence, V: Set[TokenVisit]):
        input_places = [
            in_arc.source for in_arc in eo.transition.in_arcs]
        temp_R = []
        for v in V:
            if v.token[1] in eo.event.omap:
                if self.place_mapping[v.token[0]].name in [p.name for p in input_places]:
                    temp_R.append(v)
        objs = set([v.token[1] for v in temp_R])
        R = []
        for obj in objs:
            oi_tokens = [v for v in temp_R if v.token[1] == obj]
            selected_token = max(oi_tokens, key=attrgetter('start'))
            R.append(selected_token)
        return R

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
            
            # Define values as None for further checking
            waiting, service, sojourn, sync = None, None, None, None

            if p_waiting:
                waiting = self.measure_waiting(eo, R)
                if waiting is not None and eo.transition.label in self.perf_records['waiting']:
                    self.perf_records['waiting'][eo.transition.label].append(waiting)
                elif waiting is not None:
                    self.perf_records['waiting'][eo.transition.label] = [waiting]

            if p_service:
                service = self.measure_service(eo, R)
                if service is not None and eo.transition.label in self.perf_records['service']:
                    self.perf_records['service'][eo.transition.label].append(service)
                elif service is not None:
                    self.perf_records['service'][eo.transition.label] = [service]

            if p_sojourn:
                sojourn = self.measure_sojourn(eo, R)
                if sojourn is not None and eo.transition.label in self.perf_records['sojourn']:
                    self.perf_records['sojourn'][eo.transition.label].append(sojourn)
                elif sojourn is not None:
                    self.perf_records['sojourn'][eo.transition.label] = [sojourn]

            if p_sync:
                sync = self.measure_synchronization(eo, R)
                if sync is not None and eo.transition.label in self.perf_records['synchronization']:
                    self.perf_records['synchronization'][eo.transition.label].append(sync)
                elif sync is not None:
                    self.perf_records['synchronization'][eo.transition.label] = [sync]

            if p_pooling:
                for ot in ots:
                    ot_pooling = self.measure_pooling(eo, R, ot)
                    if ot_pooling is not None and eo.transition.label in self.perf_records['pooling'][ot]:
                        self.perf_records['pooling'][ot][eo.transition.label].append(ot_pooling)
                    elif ot_pooling is not None:
                        self.perf_records['pooling'][ot][eo.transition.label] = [ot_pooling]

            if p_lagging:
                for ot in ots:
                    ot_lagging = self.measure_lagging(eo, R, ot)
                    if ot_lagging is not None and eo.transition.label in self.perf_records['lagging'][ot]:
                        self.perf_records['lagging'][ot][eo.transition.label].append(ot_lagging)
                    elif ot_lagging is not None:
                        self.perf_records['lagging'][ot][eo.transition.label] = [ot_lagging]

            if p_flow:
                if p_sojourn is not True and p_sync is True and sync is not None:
                    if p_waiting is True and p_service is not True and waiting is not None:
                        service = self.measure_service(eo, R)
                        sojourn = waiting + service if service is not None else None
                    elif p_waiting is not True and p_service is True and service is not None:
                        waiting = self.measure_waiting(eo, R)
                        sojourn = waiting + service if waiting is not None else None
                    elif waiting is None or service is None:
                        sojourn = self.measure_sojourn(eo, R)
                    flow = sojourn + sync if sojourn is not None else None
                elif p_sojourn is True and p_sync is not True and sojourn is not None:
                    sync = self.measure_synchronization(eo, R)
                    flow = sojourn + sync if sync is not None else None
                else:
                    sojourn = self.measure_sojourn(eo, R)
                    sync = self.measure_synchronization(eo, R)
                    flow = sojourn + sync if sojourn is not None and sync is not None else None

                if flow is not None and eo.transition.label in self.perf_records['flow']:
                    self.perf_records['flow'][eo.transition.label].append(flow)
                elif flow is not None:
                    self.perf_records['flow'][eo.transition.label] = [flow]



        # aggregate measures
        perf_diag = {}
        if p_waiting:
            perf_diag['agg_waiting_time'] = aggregate_perf_records(
                self.perf_records['waiting'], aggregation_measure='all')
        if p_service:
            perf_diag['agg_service_time'] = aggregate_perf_records(
                self.perf_records['service'], aggregation_measure='all')
        if p_sojourn:
            perf_diag['agg_sojourn_time'] = aggregate_perf_records(
                self.perf_records['sojourn'], aggregation_measure='all')
        if p_sync:
            perf_diag['agg_synchronization_time'] = aggregate_perf_records(
                self.perf_records['synchronization'], aggregation_measure='all')

        if p_pooling:
            perf_diag['agg_pooling_time'] = {}
            for persp in ots:
                perf_diag['agg_pooling_time'][persp] = aggregate_perf_records(
                    self.perf_records['pooling'], aggregation_measure='all', ot=persp)

        if p_lagging:
            perf_diag['agg_lagging_time'] = {}
            for persp in ots:
                perf_diag['agg_lagging_time'][persp] = aggregate_perf_records(
                    self.perf_records['lagging'], aggregation_measure='all', ot=persp)
        if p_flow:
            perf_diag['agg_flow_time'] = aggregate_perf_records(
                self.perf_records['flow'], aggregation_measure='all')
        return perf_diag

    def measure_waiting(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            waiting = (
                eo.event.vmap[ocpa_constants.DEFAULT_OCEL_START_TIMESTAMP_KEY] - min(start_times)).total_seconds()
            if waiting < 0:
                return None
            return waiting

    def measure_service(self, eo: EventOccurrence, R: Set[TokenVisit]):
        service = (
            eo.event.time - eo.event.vmap[ocpa_constants.DEFAULT_OCEL_START_TIMESTAMP_KEY]).total_seconds()
        if service < 0:
            return None
        return service

    def measure_sojourn(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            sojourn = (
                eo.event.time - min(start_times)).total_seconds()
            if sojourn < 0:
                return None
            return sojourn

    def measure_synchronization(self, eo: EventOccurrence, R: Set[TokenVisit]):
        if len(R) > 0:
            start_times = [r.start for r in R]
            sync = (max(start_times) - min(start_times)).total_seconds()
            if sync < 0:
                return None
            return sync

    def measure_pooling(self, eo: EventOccurrence, R: Set[TokenVisit], ot: str):
        ot_R = [r for r in R if r.token[1] in self.object_map[ot]]
        if len(ot_R) > 0:
            ot_start_times = [
                r.start for r in ot_R]
            pooling = (max(ot_start_times) -
                       min(ot_start_times)).total_seconds()
            if pooling < 0:
                return None
            return pooling

    def measure_lagging(self, eo: EventOccurrence, R: Set[TokenVisit], ot: str):
        ot_R = [r for r in R if r.token[1] in self.object_map[ot]]
        non_ot_R = [r for r in R if r.token[1] not in self.object_map[ot]]
        if len(ot_R) > 0 and len(non_ot_R) > 0:
            non_ot_start_times = [r.start for r in non_ot_R]
            ot_start_times = [
                r.start for r in ot_R]
            lagging = (max(ot_start_times) -
                       min(non_ot_start_times)).total_seconds()
            if lagging < 0:
                return None
            return lagging


def aggregate_stats(perf_records, elem, aggregation_measure):
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
    aggr_stat = None
    if aggregation_measure == "mean" or aggregation_measure is None:
        aggr_stat = mean(perf_records[elem])
    elif aggregation_measure == "median":
        aggr_stat = median(perf_records[elem])
    elif aggregation_measure == "stdev":
        if len(perf_records[elem]) > 1:
            aggr_stat = stdev(perf_records[elem])
        else:
            aggr_stat = None
    elif aggregation_measure == "sum":
        aggr_stat = sum(perf_records[elem])
    elif aggregation_measure == "min":
        aggr_stat = min(perf_records[elem])
    elif aggregation_measure == "max":
        aggr_stat = max(perf_records[elem])
    # aggr_stat = human_readable_stat(aggr_stat)
    return aggr_stat


def aggregate_ot_stats(perf_records, ot, elem, aggregation_measure):
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
    aggr_stat = None
    if aggregation_measure == "mean" or aggregation_measure is None:
        if ot in perf_records:
            aggr_stat = mean(perf_records[ot][elem])
    elif aggregation_measure == "median":
        if ot in perf_records:
            aggr_stat = median(perf_records[ot][elem])
    elif aggregation_measure == "stdev":
        if ot in perf_records:
            if len(perf_records[ot][elem]) > 1:
                aggr_stat = stdev(perf_records[ot][elem])
        else:
            aggr_stat = None
    elif aggregation_measure == "sum":
        if ot in perf_records:
            aggr_stat = sum(perf_records[ot][elem])
    elif aggregation_measure == "min":
        if ot in perf_records:
            aggr_stat = min(perf_records[ot][elem])
    elif aggregation_measure == "max":
        if ot in perf_records:
            aggr_stat = max(perf_records[ot][elem])
    # aggr_stat = human_readable_stat(aggr_stat)
    return aggr_stat


def aggregate_perf_records(perf_records, aggregation_measure='all', ot=None):
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
        if ot in perf_records:
            for elem in perf_records[ot].keys():
                if aggregation_measure == 'all':
                    for agg in ['mean', 'median', 'min', 'max', 'stdev']:
                        aggr_stat = aggregate_ot_stats(
                            perf_records, ot, elem, agg)
                        if elem not in aggregated_perf_records:
                            aggregated_perf_records[elem] = {}
                        aggregated_perf_records[elem][agg] = aggr_stat
                else:
                    aggr_stat = aggregate_ot_stats(
                        perf_records, ot, elem, agg)
                    if elem not in aggregated_perf_records:
                        aggregated_perf_records[elem] = {}
                    aggregated_perf_records[elem][agg] = aggr_stat
    else:

        for elem in perf_records.keys():
            if aggregation_measure == 'all':
                for agg in ['mean', 'median', 'min', 'max', 'stdev']:
                    aggr_stat = aggregate_stats(
                        perf_records, elem, agg)
                    if elem not in aggregated_perf_records:
                        aggregated_perf_records[elem] = {}
                    aggregated_perf_records[elem][agg] = aggr_stat
            else:
                aggr_stat = aggregate_stats(
                    perf_records, elem, aggregation_measure)
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
    if 'object_count' in parameters['measures']:
        p_object_count = True
    else:
        p_object_count = False
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
            transformed_diag[tr.label] = {}
            transformed_diag[tr.label]["act_freq"] = diag['act_freq'][tr.label]

            if p_object_count:
                if 'object_count' in diag:
                    transformed_diag[tr.label]['object_count'] = {ot: {agg: diag['object_count'][ot][tr.label][agg] for agg in parameters['agg'] if agg in diag['object_count'][ot][tr.label]} for ot in ocpn.object_types if tr.label in diag['object_count'][ot]}

            if p_waiting:
                if 'agg_waiting_time' in diag and tr.label in diag['agg_waiting_time']:
                    transformed_diag[tr.label]['waiting_time'] = {agg: diag['agg_waiting_time'][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_waiting_time'][tr.label]}

            if p_service:
                if 'agg_service_time' in diag and tr.label in diag['agg_service_time']:
                    transformed_diag[tr.label]['service_time'] = {agg: diag['agg_service_time'][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_service_time'][tr.label]}

            if p_sojourn:
                if 'agg_sojourn_time' in diag and tr.label in diag['agg_sojourn_time']:
                    transformed_diag[tr.label]['sojourn_time'] = {agg: diag['agg_sojourn_time'][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_sojourn_time'][tr.label]}

            if p_sync:
                if 'agg_synchronization_time' in diag and tr.label in diag['agg_synchronization_time']:
                    transformed_diag[tr.label]['synchronization_time'] = {agg: diag['agg_synchronization_time'][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_synchronization_time'][tr.label]}

            if p_pooling:
                if 'agg_pooling_time' in diag:
                    transformed_diag[tr.label]['pooling_time'] = {ot: {agg: diag['agg_pooling_time'][ot][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_pooling_time'][ot][tr.label]} for ot in ocpn.object_types if tr.label in diag['agg_pooling_time'][ot]}

            if p_lagging:
                if 'agg_lagging_time' in diag:
                    transformed_diag[tr.label]['lagging_time'] = {ot: {agg: diag['agg_lagging_time'][ot][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_lagging_time'][ot][tr.label]} for ot in ocpn.object_types if tr.label in diag['agg_lagging_time'][ot]}

            if p_flow:
                if 'agg_flow_time' in diag and tr.label in diag['agg_flow_time']:
                    transformed_diag[tr.label]['flow_time'] = {agg: diag['agg_flow_time'][tr.label][agg] for agg in parameters['agg'] if agg in diag['agg_flow_time'][tr.label]}


    transformed_diag['arc_freq'] = diag['arc_freq']

    return transformed_diag

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


def new_merge_object_count(object_count):
    merged_object_count = dict()
    for persp in object_count.keys():
        for act in object_count[persp].keys():
            persp_object_count = {act: object_count[persp][act]}
            if act not in merged_object_count.keys():
                merged_object_count[persp] = persp_object_count
            else:
                merged_object_count[persp].update(persp_object_count)
    return merged_object_count


def merge_object_count(object_count):
    merged_object_count = dict()
    for persp in object_count.keys():
        for act in object_count[persp].keys():
            persp_object_count = {persp: object_count[persp][act]}
            if act not in merged_object_count.keys():
                merged_object_count[act] = persp_object_count
            else:
                merged_object_count[act].update(persp_object_count)
    return merged_object_count


def agg_merged_object_count(merged_object_count):
    agg_merged_object_count = dict()
    for act in merged_object_count.keys():
        agg_merged_object_count[act] = dict()
        # median
        agg_merged_object_count[act]["median"] = dict()
        for persp in merged_object_count[act].keys():
            agg_merged_object_count[act]["median"][persp] = median(
                merged_object_count[act][persp])
        # mean
        agg_merged_object_count[act]["mean"] = dict()
        for persp in merged_object_count[act].keys():
            agg_merged_object_count[act]["mean"][persp] = mean(
                merged_object_count[act][persp])
        # max
        agg_merged_object_count[act]["max"] = dict()
        for persp in merged_object_count[act].keys():
            agg_merged_object_count[act]["max"][persp] = mean(
                merged_object_count[act][persp])

        # min
        agg_merged_object_count[act]["min"] = dict()
        for persp in merged_object_count[act].keys():
            agg_merged_object_count[act]["min"][persp] = mean(
                merged_object_count[act][persp])

    return agg_merged_object_count
