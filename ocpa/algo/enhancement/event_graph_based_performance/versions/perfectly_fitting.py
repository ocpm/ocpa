from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Subprocess
from ocpa.objects.graph.correlated_event_graph.obj import CorrelatedEventGraph
from ocpa.objects.log.obj import Event
from ocpa.algo.util.util import AGG_MAP
from ocpa.util.vis_util import human_readable_stat
from ocpa.algo.filtering.graph.event_graph import algorithm as event_graph_filtering_factory

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

    if 'selected_object_types' in parameters:
        selected_object_types = parameters['selected_object_types']
    else:
        selected_object_types = None

    if perf_metric == "service":
        records = compute_service_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "waiting":
        records = compute_waiting_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "sojourn":
        records = compute_sojourn_time(cegs, sp)
        return human_readable_stat(AGG_MAP[agg](records))
    elif perf_metric == "synchronization":
        records = compute_sync_time(cegs, sp, selected_object_types)
        return human_readable_stat(AGG_MAP[agg](records))
    # elif perf_metric == "coherent_synchronization":
    #     object_types = ocpn.object_types
    #     result = {}
    #     for ot in object_types:
    #         result[ot] = human_readable_stat(
    #             AGG_MAP[agg](compute_coherent_sync_time(cegs, ot, sp)))
    #     return result
    # elif perf_metric == "inherent_synchronization":
    #     object_types = ocpn.object_types
    #     result = {}
    #     for ot in object_types:
    #         result[ot] = {}
    #         for ot2 in object_types:
    #             if ot == ot2:
    #                 continue
    #             result[ot][ot2] = human_readable_stat(AGG_MAP[agg](
    #                 compute_inherent_sync_time(cegs, ot, ot2, sp)))
    #     return result
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
    elif perf_metric == "absolute_object_type_freq":
        return compute_abs_object_type_freq(cegs, sp)
    elif perf_metric == "object_type_freq":
        return AGG_MAP[agg](compute_object_type_freq(cegs, sp))
    elif perf_metric == "absolute_inter_act_freq":
        return compute_abs_inter_act_freq(cegs, sp)
    elif perf_metric == "inter_act_freq":
        return AGG_MAP[agg](compute_inter_act_freq(cegs, sp))
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
    if events == None:
        return None
    events = list(events)
    event_timestamps = [e.time for e in events]
    i = event_timestamps.index(max(event_timestamps))
    return events[i]


def compute_waiting_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_waiting_times = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        first_event = first(filtered_ceg.graph.nodes)
        last_context_event = last(
            initial_ceg.get_event_context(first_event))
        if first_event is not None and last_context_event is not None:
            if first_event.vmap["start_timestamp"] is not None:
                waiting_time = (
                    first_event.vmap["start_timestamp"] - last_context_event.time).total_seconds()
            else:
                waiting_time = (first_event.time -
                                last_context_event.time).total_seconds()
            all_waiting_times.append(waiting_time)
    if len(all_waiting_times) == 0:
        return [0]
    else:
        return all_waiting_times


def compute_service_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_service_times = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        last_event = last(filtered_ceg.graph.nodes)
        first_event = first(filtered_ceg.graph.nodes)
        if last_event is not None and first_event is not None:
            if first_event.vmap["start_timestamp"] is not None:
                service_time = (last_event.time -
                                first_event.vmap["start_timestamp"]).total_seconds()
            else:
                service_time = (last_event.time -
                                first_event.time).total_seconds()
            all_service_times.append(service_time)
    if len(all_service_times) == 0:
        return [0]
    else:
        return all_service_times

    # return [(last(ceg.graph.nodes).time - first(ceg.graph.nodes).time).total_seconds() for ceg in cegs]


def compute_sojourn_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    all_sojourn_times = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        last_event = last(filtered_ceg.graph.nodes)
        last_context_event = last(
            initial_ceg.get_event_context(first(filtered_ceg.graph.nodes)))
        if last_event is not None:
            # if the event is the first event, no context, but we can still use the first event.
            if last_context_event is None:
                last_context_event = first(filtered_ceg.graph.nodes)
            print("Sojourn Time between {} -> {}: {}".format(last_context_event.act,
                  last_event.act, (last_event.time - last_context_event.time).total_seconds()))
            all_sojourn_times.append(
                (last_event.time - last_context_event.time).total_seconds())
    if len(all_sojourn_times) == 0:
        return [0]
    else:
        return all_sojourn_times


def compute_sync_time(cegs: List[CorrelatedEventGraph], sp: Subprocess = None, selected_object_types=None):
    all_sync_times = []
    for initial_ceg in cegs:
        if selected_object_types == None:
            raise ValueError(
                "Provide selected object types, e.g., (Order,Item)")
        elif type(selected_object_types) == tuple:
            raise ValueError(
                "Provide selected object types in tuple, e.g., (Order,Item)")
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        first_event = first(filtered_ceg.graph.nodes)
        last_context_event_ot1 = last(
            initial_ceg.get_event_context_per_object(first_event, selected_object_types[0]))
        last_context_event_ot2 = last(
            initial_ceg.get_event_context_per_object(first_event, selected_object_types[1]))
        if last_context_event_ot1 is not None and last_context_event_ot2 is not None:
            all_sync_times.append(
                abs((last_context_event_ot1.time - last_context_event_ot2.time).total_seconds()))
    if len(all_sync_times) == 0:
        return [0]
    else:
        return all_sync_times


# def compute_coherent_sync_time(cegs: List[CorrelatedEventGraph], ot, sp: Subprocess = None):
#     all_coherent_sync_times = []
#     for initial_ceg in cegs:
#         if sp == None:
#             filtered_ceg = initial_ceg
#         else:
#             filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
#             if filtered_ceg == None:
#                 continue
#         first_event = first(filtered_ceg.graph.nodes)
#         if len([oi for oi in first_event.omap if ot == filtered_ceg.ovmap[oi].type]) < 2:
#             continue
#         last_ot_context_event = last(
#             initial_ceg.get_event_context_per_object(first_event, ot))
#         first_ot_context_event = first(
#             initial_ceg.get_event_context_per_object(first_event, ot))
#         if last_ot_context_event is not None and first_ot_context_event is not None:
#             all_coherent_sync_times.append(
#                 abs((last_ot_context_event.time - first_ot_context_event.time).total_seconds()))

#     if len(all_coherent_sync_times) == 0:
#         return [0]
#     else:
#         return all_coherent_sync_times


# def compute_inherent_sync_time(cegs: List[CorrelatedEventGraph], ot, ot2, sp: Subprocess = None):
#     all_inherent_sync_times = []
#     for initial_ceg in cegs:
#         if sp == None:
#             filtered_ceg = initial_ceg
#         else:
#             filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
#             if filtered_ceg == None:
#                 continue
#         first_event = first(filtered_ceg.graph.nodes)
#         obj_types = set(
#             [filtered_ceg.ovmap[oi].type for oi in first_event.omap])
#         if ot in obj_types and ot2 in obj_types:
#             last_ot_context_event = last(
#                 initial_ceg.get_event_context_per_object(first_event, ot))
#             last_ot2_context_event = last(
#                 initial_ceg.get_event_context_per_object(first_event, ot2))
#             if last_ot_context_event is not None and last_ot2_context_event is not None:
#                 all_inherent_sync_times.append(
#                     abs((last_ot_context_event.time - last_ot2_context_event.time).total_seconds()))
#         else:
#             continue
#     if len(all_inherent_sync_times) == 0:
#         return [0]
#     else:
#         return all_inherent_sync_times


def compute_absolute_frequency(cegs: List[CorrelatedEventGraph], sp: Subprocess = None):
    if sp == None:
        return len([initial_ceg for initial_ceg in cegs])
    else:
        return len([event_graph_filtering_factory.apply(sp, initial_ceg) for initial_ceg in cegs])


def compute_object_frequency_per_type(cegs: List[CorrelatedEventGraph], ot, sp: Subprocess = None) -> Event:
    object_freqs = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        freq = len(set(
            [oi for e in filtered_ceg.graph.nodes for oi in e.omap if filtered_ceg.ovmap[oi].type == ot]))
        object_freqs.append(freq)
    if len(object_freqs) == 0:
        return [0]
    else:
        return object_freqs


# def compute_object_frequency_per_type(cegs: List[CorrelatedEventGraph], object_types, sp: Subprocess = None):
#     return {ot: [compute_object_freq_in_ceg(ceg, ot) for ceg in cegs] for ot in object_types}


def compute_object_type_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    object_type_freqs = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        obj_type_freq = len(set(
            [filtered_ceg.ovmap[oi].type for e in filtered_ceg.graph.nodes for oi in e.omap]))
        object_type_freqs.append(obj_type_freq)
    if len(object_type_freqs) == 0:
        return [0]
    else:
        return object_type_freqs


def compute_abs_object_type_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    if sp == None:
        return len(set(
            [initial_ceg.ovmap[oi].type for initial_ceg in cegs for e in initial_ceg.graph.nodes for oi in e.omap]))
    else:
        return len(set(
            [initial_ceg.ovmap[oi].type for initial_ceg in cegs if event_graph_filtering_factory.apply(sp, initial_ceg) != None for e in event_graph_filtering_factory.apply(sp, initial_ceg).graph.nodes for oi in e.omap]))


def compute_inter_act_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    inter_act_freqs = []
    for initial_ceg in cegs:
        if sp == None:
            filtered_ceg = initial_ceg
        else:
            filtered_ceg = event_graph_filtering_factory.apply(sp, initial_ceg)
            if filtered_ceg == None:
                continue
        inter_acts = set()
        for e in filtered_ceg.graph.nodes:
            obj_types = set()
            for oi in e.omap:
                obj_types.add(filtered_ceg.ovmap[oi].type)
            if len(obj_types) > 1:
                inter_acts.add(e.act)
        inter_act_freq = len(inter_acts)
        inter_act_freqs.append(inter_act_freq)
    if len(inter_act_freqs) == 0:
        return [0]
    else:
        return inter_act_freqs

    # if sp == None:
    #     return len(set(
    #         [e.act for initial_ceg in cegs for e in initial_ceg.graph.nodes if len(e.omap) >= 2]))
    # else:
    #     return len(set(
    #         [e.act for initial_ceg in cegs if event_graph_filtering_factory.apply(sp, initial_ceg) != None for e in event_graph_filtering_factory.apply(sp, initial_ceg).graph.nodes if len(e.omap) >= 2]))


def compute_abs_inter_act_freq(cegs: List[CorrelatedEventGraph], sp: Subprocess = None) -> Event:
    return max(compute_inter_act_freq(cegs, sp))
