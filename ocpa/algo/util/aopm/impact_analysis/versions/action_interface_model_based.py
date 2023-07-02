import datetime
import pandas as pd
from ocpa.objects.aopm.action_interface_model.obj import OperationalState
from ocpa.objects.aopm.impact.obj import ActionChange, FunctionWiseStructuralImpact, ObjectWiseStructuralImpact, OperationalImpact, FunctionWisePerformanceImpact, ObjectWisePerformanceImpact
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Marking

from typing import List, Dict, Any, Optional, Set, Tuple, Union
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl
from ocpa.algo.enhancement.token_replay_based_performance.util import run_timed_replay
from ocpa.algo.util.util import project_log
from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory
from ocpa.algo.util.filtering.log import time_filtering
from ocpa.algo.enhancement.ocpn_analysis.projection import algorithm as projection_factory

def apply(ac: ActionChange, ocel, comp_tw: Tuple[datetime.datetime, datetime.datetime]):
    results = {}
    object_types = ac.aim.ocpn.object_types

    results['SA'] = {}
    results['SA']['Function'] = {}
    results['SA']['Function']['Prior'] = {}
    for ot in object_types:
        # print(ot, 'BP_FSA', backward_pass_FSA(ac, ot).quantify())
        results['SA']['Function']['Prior'][ot] = backward_pass_FSA(ac, ot).quantify()

    results['SA']['Function']['Posterior'] = {}
    for ot in object_types:
        # print(ot, 'FP_FSA', forward_pass_FSA(ac, ot).quantify())
        results['SA']['Function']['Posterior'][ot] = forward_pass_FSA(ac, ot).quantify()

    results['SA']['Object'] = {}
    # print('direct_OSA', direct_OSA(ac).quantify())
    results['SA']['Object']['Direct'] = direct_OSA(ac).quantify()
    # print('BP_OSA', backward_pass_OSA(ac).quantify())
    results['SA']['Object']['Prior'] = backward_pass_OSA(ac).quantify()
    # print('FP_OSA', forward_pass_OSA(ac).quantify())
    results['SA']['Object']['Posterior'] = forward_pass_OSA(ac).quantify()

    filtered_ocel = time_filtering.events(ocel, ac.tw[0], ac.tw[1])
    marking, token_history = new_compute_marking(filtered_ocel, ac.aim.ocpn)
    # print(marking)
    os = OperationalState(ac.aim, marking, {})

    results['OIA'] = {}
    results['OIA']['Posterior'] = {}
    for ot in object_types:
        results['OIA']['Posterior'][ot] = forward_pass_OIA(
            ac, os, ot).quantify()
        # print(ot, 'BP_OIA', backward_pass_OIA(ac, os, ot).quantify())

    results['OIA']['Prior'] = {}
    for ot in object_types:
        results['OIA']['Prior'][ot] = backward_pass_OIA(
            ac, os, ot).quantify()
        # print(ot, 'FP_OIA', forward_pass_OIA(ac, os, ot).quantify())

    results['FPA'] = {}
    results['OPA'] = {}
    for t in ac.transitions:
        results['FPA'][t.label] = {}
        for measure in ['flow', 'sojourn', 'syncronization']:
            agg = 'avg'
            results['FPA'][t.label][measure] = FPA(t.label, ac.tw, comp_tw, ocel, measure, agg)
        for measure in ['pooling', 'lagging', 'rediness']:
            agg = 'avg'
            results['FPA'][t.label][measure] = {}
            for ot in object_types:
                results['FPA'][t.label][measure][ot] = FPA(t.label, ac.tw, comp_tw, ocel, measure, agg, ot)

        results['OPA'][t.label] = {}
        for ot in object_types:
            results['OPA'][t.label][ot] = {}
            for measure in ['object_freq']:
                agg = 'sum'
                results['OPA'][t.label][ot][measure] = OPA(t.label, ac.tw, comp_tw, ocel, measure, agg, ot)
            for measure in ['elapsed', 'remaining']:
                agg = 'avg'
                results['OPA'][t.label][ot][measure] = OPA(t.label, ac.tw, comp_tw, ocel, measure, agg, ot)
    return results


def type_specific_FSA(change: ActionChange, ot: str) -> FunctionWiseStructuralImpact:
    return FunctionWiseStructuralImpact(set([t for t in change.transitions if ot in [p.object_type for p in t.preset]]))


# def backward_pass_FSA(change: ActionChange) -> FunctionWiseStructuralImpact:
#     return FunctionWiseStructuralImpact(set([t2 for t in change.transitions for t2 in change.aim.ocpn.backward_pass(t)]))


def backward_pass_FSA(change: ActionChange, ot: str) -> FunctionWiseStructuralImpact:
    ancestor_transitions = set()
    for t in change.transitions:
        ancestor_transitions = ancestor_transitions | set([t2 for t2 in change.aim.ocpn.ancestor_transitions(
            t, ot) if t2.silent == False])
    return FunctionWiseStructuralImpact(ancestor_transitions)


def forward_pass_FSA(change: ActionChange, ot: str) -> FunctionWiseStructuralImpact:
    descendant_transitions = set()
    for t in change.transitions:
        descendant_transitions = descendant_transitions | set([t2 for t2 in change.aim.ocpn.descendant_transitions(
            t, ot) if t2.silent == False])
    return FunctionWiseStructuralImpact(descendant_transitions)


def direct_OSA(change: ActionChange) -> ObjectWiseStructuralImpact:
    return ObjectWiseStructuralImpact(set([ot for t in change.transitions for ot in [p.object_type for p in t.preset]]))


def backward_pass_OSA(change: ActionChange) -> ObjectWiseStructuralImpact:
    ancestor_places = set()
    for t in change.transitions:
        for ot in change.aim.ocpn.object_types:
            ancestor_places = ancestor_places | change.aim.ocpn.ancestor_places(
                t, ot)
    return ObjectWiseStructuralImpact(set([ot for ot in [p.object_type for p in ancestor_places]]))


def forward_pass_OSA(change: ActionChange) -> ObjectWiseStructuralImpact:
    descendant_places = set()
    for t in change.transitions:
        for ot in change.aim.ocpn.object_types:
            descendant_places = descendant_places | change.aim.ocpn.descendant_places(
                t, ot)
    return ObjectWiseStructuralImpact(set([ot for ot in [p.object_type for p in descendant_places]]))


# def preceding_OIA(change: ActionChange, os: OperationalState, ot: str) -> OperationalImpact:
#     objects = []
#     for t in change.transitions:
#         print(t, t.preset)
#         objects += [oi for p,
#                     oi in os.marking.tokens if p in t.preset and p.object_type == ot]
#     return OperationalImpact(set(objects))


# def following_OIA(change: ActionChange, os: OperationalState, ot: str) -> OperationalImpact:
#     objects = []
#     for t in change.transitions:
#         objects += [oi for p,
#                     oi in os.marking.tokens if p in t.postset and p.object_type == ot]
#     return OperationalImpact(set(objects))


def backward_pass_OIA(change: ActionChange, os: OperationalState, ot: str) -> OperationalImpact:
    objects = {}
    for t in change.transitions:
        for t2 in change.aim.ocpn.ancestor_transitions(t, ot):
            if t2.silent == False:
                project_parameters = {'source': t2.label,
                                      'target': t.label, 'object_type': ot}
                subnet = projection_factory.apply(change.aim.ocpn, variant="subprocess",
                                                  parameters=project_parameters)

                objects[t2] = set([token[1] for token,
                                   count in os.marking.items() if token[0] in subnet.places])
                # print(t2, subnet.places, len(objects[t2]))
    return OperationalImpact(objects)


def forward_pass_OIA(change: ActionChange, os: OperationalState, ot: str) -> OperationalImpact:
    objects = {}
    for t in change.transitions:
        for t2 in change.aim.ocpn.descendant_transitions(t, ot):
            if t2.silent == False:
                project_parameters = {'source': t.label,
                                      'target': t2.label, 'object_type': ot}
                subnet = projection_factory.apply(change.aim.ocpn, variant="subprocess",
                                                  parameters=project_parameters)
                objects[t2] = set([token[1] for token,
                                   count in os.marking.items() if token[0] in subnet.places])
    return OperationalImpact(objects)


def compute_marking(ocel, ocpn: ObjectCentricPetriNet):
    marking = Marking()
    for i, row in ocel.log.log.iterrows():
        activity = row["event_activity"]
        for tr in ocpn.transitions:
            if tr.label == activity:
                for arc in tr.out_arcs:
                    pl = arc.target
                    ois = row[pl.object_type]
                    for oi in ois:
                        if not pd.isna(oi):
                            marking.add_token(pl, oi)
                break
    return marking, '_'


def new_compute_marking(ocel, ocpn: ObjectCentricPetriNet):
    df = succint_mdl_to_exploded_mdl(ocel.log.log)
    marking = Marking()
    token_history = {}
    for persp in ocpn.object_types:
        net, im, fm = ocpn.nets[persp]
        print(df)
        log = project_log(df, persp)
        replay_results = run_timed_replay(log, net, im, fm)
        for result in replay_results:
            token_id = result['trace_id']
            reached_marking = result['reached_marking']
            activated_transitions = result['activated_transitions']
            # print(token_id, [(ocpn.place_mapping[p[0]], token_id)
            #       for p in reached_marking.items()])
            for p in reached_marking.items():
                marking += {(ocpn.place_mapping[p[0]], token_id): p[1]}
                # marking.add_token()
                token_history[token_id] = activated_transitions
    return marking, token_history


def FPA(activity_name: str, change_tw: Tuple[datetime.datetime, datetime.datetime], comp_tw: Tuple[datetime.datetime, datetime.datetime], ocel, measure, agg, ot=None) -> FunctionWisePerformanceImpact:
    change_log = time_filtering.events(ocel, change_tw[0], change_tw[1])
    comp_log = time_filtering.events(ocel, comp_tw[0], comp_tw[1])
    perf_diff_dict = {}
    try:
        perf_parameters = {'measure': measure,
                        'activity': activity_name, 'aggregation': agg, 'object_type': ot}
        change_metric = performance_factory.apply(
            change_log, variant='event_object_graph_based', parameters=perf_parameters)
        comp_metric = performance_factory.apply(
            comp_log, variant='event_object_graph_based', parameters=perf_parameters)
        return comp_metric - change_metric
    except:
        return None
        


def OPA(activity_name: str, change_tw: Tuple[datetime.datetime, datetime.datetime], comp_tw: Tuple[datetime.datetime, datetime.datetime], ocel, measure, agg, ot) -> ObjectWisePerformanceImpact:
    change_log = time_filtering.events(ocel, change_tw[0], change_tw[1])
    comp_log = time_filtering.events(ocel, comp_tw[0], comp_tw[1])
    try:
        perf_parameters = {'measure': measure,
                            'activity': activity_name, 'aggregation': agg, 'object_type': ot}
        change_metric = performance_factory.apply(
            change_log, variant='event_object_graph_based', parameters=perf_parameters)
        comp_metric = performance_factory.apply(
            comp_log, variant='event_object_graph_based', parameters=perf_parameters)
        return change_metric - comp_metric
    except:
        return  None
