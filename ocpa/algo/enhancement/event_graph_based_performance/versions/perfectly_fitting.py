from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Subprocess
from ocpa.objects.correlated_event_graph.obj import CorrelatedEventGraph
from ocpa.objects.log.obj import Event
from ocpa.algo.util.util import AGG_MAP
from ocpa.util.vis_util import human_readable_stat
from ocpa.algo.filtering.event_graph import algorithm as event_graph_filtering_factory

from typing import List, Set


def apply(ocpn: ObjectCentricPetriNet, cegs, parameters):

    if parameters == None:
        parameters = dict()

    if 'subprocess' in parameters:
        sp = parameters['subprocess']
    else:
        sp = None

    if 'perf_metric' in parameters:
        perf_metric = parameters['perf_metric']
    else:
        perf_metric = "throughput"

    if 'agg' in parameters:
        agg = parameters['agg']
    else:
        agg = "avg"

    if perf_metric == "throughput":
        records = compute_throughput_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "waiting":
        records = compute_waiting_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "sojourn":
        records = compute_sojourn_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "synchronization":
        records = compute_sync_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "coherent_synchronization":
        object_types = ocpn.object_types
        result = {}
        for ot in object_types:
            result[ot] = human_readable_stat(
                AGG_MAP[agg](compute_coherent_sync_time(cegs, ot, sp)))
        return result
    elif perf_metric == "inherent_synchronization":
        object_types = ocpn.object_types
        result = {}
        for ot in object_types:
            result[ot] = {}
            for ot2 in object_types:
                if ot == ot2:
                    continue
                result[ot][ot2] = human_readable_stat(AGG_MAP[agg](
                    compute_inherent_sync_time(cegs, ot, ot2, sp)))
        return result
    elif perf_metric == "absolute_freq":
        return compute_absolute_frequency(cegs)
    elif perf_metric == "object_freq":
        object_types = ocpn.object_types
        result = {}
        for ot in object_types:
            result[ot] = AGG_MAP[agg](
                compute_object_frequency_per_type(cegs, ot, sp))
        # records = compute_object_frequency_per_type(cegs, object_types, sp)
        # result = {ot: AGG_MAP[agg](records[ot]) for ot in object_types}
        return result
    elif perf_metric == "object_type_freq":
        return compute_object_type_freq(cegs, sp)
    elif perf_metric == "interacting_act_freq":
        return compute_interacting_act_freq(cegs, sp)
    else:
        raise ValueError("Will be introduced soon :)")


def first(events: Set[Event]) -> Event:
    if len(events) == 0:
        return None
    events = list(events)
    event_timestamps = [e.time for e in events]
    i = event_timestamps.index(min(event_timestamps))
    return events[i]


def last(events: Set[Event]) -> Event:
    if len(events) == 0:
        return None
    events = list(events)
    event_timestamps = [e.time for e in events]
    i = event_timestamps.index(max(event_timestamps))
    return events[i]


def compute_waiting_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_waiting_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        first_event = first(ceg.graph.nodes)
        last_context_event = last(
            initial_ceg.get_event_context(first(ceg.graph.nodes)))
        if first_event is not None and last_context_event is not None:
            all_waiting_times.append(
                (first_event.time - last_context_event.time).total_seconds())
    if len(all_waiting_times) == 0:
        return [0]
    else:
        return all_waiting_times

    # return [(first(ceg.graph.nodes).time - last(ceg.get_event_context(first(ceg.graph.nodes)))).total_seconds() for ceg in cegs if first(ceg.graph.nodes) is not None and last(ceg.get_event_context(first(ceg.graph.nodes))) is not None]


def compute_throughput_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_throughput_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        last_event = last(ceg.graph.nodes)
        first_event = first(ceg.graph.nodes)
        if last_event is not None and first_event:
            all_throughput_times.append(
                (last_event.time - first_event.time).total_seconds())
    if len(all_throughput_times) == 0:
        return [0]
    else:
        return all_throughput_times

    # return [(last(ceg.graph.nodes).time - first(ceg.graph.nodes).time).total_seconds() for ceg in cegs]


def compute_sojourn_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_sojourn_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        last_event = last(ceg.graph.nodes)
        last_context_event = last(
            initial_ceg.get_event_context(first(ceg.graph.nodes)))
        if last_event is not None and last_context_event is not None:
            all_sojourn_times.append(
                (last_event.time - last_context_event.time).total_seconds())
    if len(all_sojourn_times) == 0:
        return [0]
    else:
        return all_sojourn_times

    # return [(last(ceg.graph.nodes).time - last(ceg.get_event_context(first(ceg.graph.nodes))).time).total_seconds() for ceg in cegs]


def compute_sync_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_sync_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        first_event = first(ceg.graph.nodes)
        last_context_event = last(
            initial_ceg.get_event_context(first_event))
        first_context_event = first(
            initial_ceg.get_event_context(first_event))
        if last_context_event is not None and first_context_event is not None:
            all_sync_times.append(
                abs((last_context_event.time - first_context_event.time).total_seconds()))
    if len(all_sync_times) == 0:
        return [0]
    else:
        return all_sync_times

    # return [abs((last(ceg.get_event_context(first(ceg))).time - first(ceg.get_event_context(first(ceg.graph.nodes))).time).total_seconds()) for ceg in cegs]


def compute_coherent_sync_time(cegs: List[CorrelatedEventGraph], ot, sp: Subprocess = None):
    all_coherent_sync_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        first_event = first(ceg.graph.nodes)
        if len([oi for oi in first_event.omap if ot == ceg.ovmap[oi].type]) < 2:
            continue
        last_ot_context_event = last(
            initial_ceg.get_event_context_per_object(first_event, ot))
        first_ot_context_event = first(
            initial_ceg.get_event_context_per_object(first_event, ot))
        if last_ot_context_event is not None and first_ot_context_event is not None:
            all_coherent_sync_times.append(
                abs((last_ot_context_event.time - first_ot_context_event.time).total_seconds()))

    if len(all_coherent_sync_times) == 0:
        return [0]
    else:
        return all_coherent_sync_times


def compute_inherent_sync_time(cegs: List[CorrelatedEventGraph], ot, ot2, sp: Subprocess = None):
    all_inherent_sync_times = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        first_event = first(ceg.graph.nodes)
        obj_types = set([ceg.ovmap[oi].type for oi in first_event.omap])
        if ot in obj_types and ot2 in obj_types:
            last_ot_context_event = last(
                initial_ceg.get_event_context_per_object(first_event, ot))
            last_ot2_context_event = last(
                initial_ceg.get_event_context_per_object(first_event, ot2))
            if last_ot_context_event is not None and last_ot2_context_event is not None:
                all_inherent_sync_times.append(
                    abs((last_ot_context_event.time - last_ot2_context_event.time).total_seconds()))
        else:
            continue
    if len(all_inherent_sync_times) == 0:
        return [0]
    else:
        return all_inherent_sync_times


def compute_absolute_frequency(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    if sp == None:
        return len([initial_ceg for initial_ceg in cegs])
    else:
        return len([event_graph_filtering_factory.apply(sp, initial_ceg) for initial_ceg in cegs])


def compute_object_frequency_per_type(cegs: List[CorrelatedEventGraph], ot, sp: Subprocess = None) -> Event:
    object_freqs = []
    for initial_ceg in cegs:
        if sp == None:
            ceg = initial_ceg
        else:
            ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
        freq = len(set(
            [oi for e in ceg.graph.nodes for oi in e.omap if ceg.ovmap[oi].type == ot]))
        object_freqs.append(freq)
    if len(object_freqs) == 0:
        return [0]
    else:
        return object_freqs


# def compute_object_frequency_per_type(cegs: List[CorrelatedEventGraph], object_types, sp: Subprocess = None):
#     return {ot: [compute_object_freq_in_ceg(ceg, ot) for ceg in cegs] for ot in object_types}


def compute_object_type_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    if sp == None:
        return len(set(
            [initial_ceg.ovmap[oi].type for initial_ceg in cegs for e in initial_ceg.graph.nodes for oi in e.omap]))
    else:
        return len(set(
            [initial_ceg.ovmap[oi].type for initial_ceg in cegs for e in event_graph_filtering_factory.apply(sp, initial_ceg).graph.nodes for oi in e.omap]))


def compute_interacting_act_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    if sp == None:
        return len(set(
            [e.act for initial_ceg in cegs for e in initial_ceg.graph.nodes if len(e.omap) >= 2]))
    else:
        return len(set(
            [e.act for initial_ceg in cegs for e in event_graph_filtering_factory.apply(sp, initial_ceg).graph.nodes if len(e.omap) >= 2]))
