import datetime
import pandas as pd
from ocpa.objects.aopm.action_interface_model.obj import ActionInterfaceModel, Configuration, ActionInstance, IntegrityRuleBasedAction, ReactionRuleBasedAction, OperationalState
from ocpa.objects.aopm.impact.obj import ActionChange, FunctionWiseStructuralImpact, ObjectWiseStructuralImpact, OperationalImpact, FunctionWisePerformanceImpact, ObjectWisePerformanceImpact
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Marking
from ocpa.objects.log.ocel import OCEL
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl
from ocpa.algo.enhancement.token_replay_based_performance.util import run_timed_replay, apply_trace, single_element_statistics
from ocpa.algo.util.util import project_log
from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory
from ocpa.algo.util.filtering.log import time_filtering


def apply(ai: ActionInstance, config: Configuration, ocel: OCEL, tw: Tuple[datetime.datetime, datetime.datetime], parameters):
    if parameters is None:
        parameters = {}
    ac = detect_change(ai, config)
    object_types = config.aim.ocpn.object_types
    for ot in object_types:
        print(type_specific_FSA(ac, ot))
    print(backward_pass_FSA(ai.aim, ac))
    print(forward_pass_FSA(ai.aim, ac))
    print(direct_OSA(ai.aim, ac))
    print(backward_pass_OSA(ai.aim, ac))
    print(forward_pass_OSA(ai.aim, ac))
    marking = new_compute_marking(ocel, ai.aim.ocpn)
    os = OperationalState(ai.aim, marking, {})
    print(preceding_OIA(ai.aim, ac, os))
    print(following_OIA(ai.aim, ac, os))
    print(backward_pass_OIA(ai.aim, ac, os))
    print(forward_pass_OIA(ai.aim, ac, os))
    for measure in ['flow', 'sojourn', 'syncronization']:
        agg = 'avg'
        print(measure, agg)
        print(FPI(ai.aim, ac, tw, ocel, measure, agg))

    for ot in object_types:
        for measure in ['pooling', 'lagging', 'readying', 'elapsed', 'remaining']:
            agg = 'avg'
            print(measure, agg, ot)
            print(FPI(ai.aim, ac, tw, ocel, measure, agg, ot))

    for ot in object_types:
        for measure in ['elapsed', 'remaining']:
            agg = 'avg'
            print(measure, agg, ot)
            print(OPI(ai.aim, ac, tw, ocel, measure, agg, ot))


def apply_v2(ac: ActionChange, ocel: OCEL, tw: Tuple[datetime.datetime, datetime.datetime], parameters=None):
    if parameters is None:
        parameters = {}
    object_types = ac.aim.ocpn.object_types
    # for ot in object_types:
    #     print(type_specific_FSA(ac, ot))
    print(backward_pass_FSA(ac))
    print(forward_pass_FSA(ac.aim, ac))
    print(direct_OSA(ac.aim, ac))
    print(backward_pass_OSA(ac.aim, ac))
    print(forward_pass_OSA(ac.aim, ac))
    filtered_ocel = time_filtering.events(ocel, ac.tw[0], ac.tw[1])
    marking = new_compute_marking(filtered_ocel, ac.aim.ocpn)
    os = OperationalState(ac.aim, marking, {})
    print(preceding_OIA(ac.aim, ac, os))
    print(following_OIA(ac.aim, ac, os))
    print(backward_pass_OIA(ac.aim, ac, os))
    print(forward_pass_OIA(ac.aim, ac, os))
    for measure in ['flow', 'sojourn', 'syncronization']:
        agg = 'avg'
        print(measure, agg)
        print(FPI(ac.aim, ac, tw, ocel, measure, agg))

    for ot in object_types:
        for measure in ['pooling', 'lagging', 'readying', 'elapsed', 'remaining']:
            agg = 'avg'
            print(measure, agg, ot)
            print(FPI(ac.aim, ac, tw, ocel, measure, agg, ot))

    for ot in object_types:
        for measure in ['elapsed', 'remaining']:
            agg = 'avg'
            print(measure, agg, ot)
            print(OPI(ac.aim, ac, tw, ocel, measure, agg, ot))


def detect_change(ai: ActionInstance, config: Configuration):
    new_config = ai.action.apply(config)
    if type(ai.action) == IntegrityRuleBasedAction:
        T = []
        for t in config.integrity_rule_assignment:
            if t not in new_config.integrity_rule_assignment:
                T.append(t)
            elif config.integrity_rule_assignment[t] != new_config.integrity_rule_assignment[t]:
                T.append(t)
            else:
                continue
        for t in new_config.integrity_rule_assignment:
            if t not in config.integrity_rule_assignment:
                T.append(t)
            elif new_config.integrity_rule_assignment[t] != config.integrity_rule_assignment[t]:
                T.append(t)
            else:
                continue
        return ActionChange(ai.aim, set(T), ai.time_window)


def type_specific_FSA(change: ActionChange, ot: str) -> FunctionWiseStructuralImpact:
    return FunctionWiseStructuralImpact(set([t for t in change.transitions if ot in [p.object_type for p in t.preset]]))


def backward_pass_FSA(change: ActionChange) -> FunctionWiseStructuralImpact:
    for t in change.transitions:
        print(change.aim.ocpn.backward_pass(t))
    return FunctionWiseStructuralImpact(set([t2 for t in change.transitions for t2 in change.aim.ocpn.backward_pass(t)]))


def forward_pass_FSA(aim: ActionInterfaceModel, change: ActionChange) -> FunctionWiseStructuralImpact:
    return FunctionWiseStructuralImpact(set([t2 for t in change.transitions for t2 in aim.ocpn.forward_pass(t)]))


def direct_OSA(aim: ActionInterfaceModel, change: ActionChange) -> ObjectWiseStructuralImpact:
    return ObjectWiseStructuralImpact(set([ot for t in change.transitions for ot in [p.object_type for p in t.preset]]))


def backward_pass_OSA(aim: ActionInterfaceModel, change: ActionChange) -> ObjectWiseStructuralImpact:
    return ObjectWiseStructuralImpact(set([ot for t in change.transitions for t2 in aim.ocpn.backward_pass(t) for ot in [p.object_type for p in t2.preset]]))


def forward_pass_OSA(aim: ActionInterfaceModel, change: ActionChange) -> ObjectWiseStructuralImpact:
    return ObjectWiseStructuralImpact(set([ot for t in change.transitions for t2 in aim.ocpn.forward_pass(t) for ot in [p.object_type for p in t2.postset]]))


def preceding_OIA(aim: ActionInterfaceModel, change: ActionChange, os: OperationalState) -> OperationalImpact:
    objects = []
    for t in change.transitions:
        objects += [oi for p, oi in os.marking.tokens if p in t.preset]
    return OperationalImpact(set(objects))


def following_OIA(aim: ActionInterfaceModel, change: ActionChange, os: OperationalState) -> OperationalImpact:
    objects = []
    for t in change.transitions:
        objects += [oi for p, oi in os.marking.tokens if p in t.postset]
    return OperationalImpact(set(objects))


def backward_pass_OIA(aim: ActionInterfaceModel, change: ActionChange, os: OperationalState) -> OperationalImpact:
    objects = []
    for t in change.transitions:
        for t2 in aim.ocpn.backward_pass(t):
            objects += [oi for p, oi in os.marking.tokens if p in t2.preset]
    return OperationalImpact(set(objects))


def forward_pass_OIA(aim: ActionInterfaceModel, change: ActionChange, os: OperationalState) -> OperationalImpact:
    objects = []
    for t in change.transitions:
        for t2 in aim.ocpn.forward_pass(t):
            objects += [oi for p, oi in os.marking.tokens if p in t2.postset]
    return OperationalImpact(set(objects))


def compute_marking(ocel: OCEL, ocpn: ObjectCentricPetriNet):
    marking = Marking()
    for i, row in ocel.log.log.iterrows():
        activity = row["event_activity"]
        for tr in ocpn.transitions:
            if tr.name == activity:
                for arc in tr.out_arcs:
                    pl = arc.target
                    ois = row[pl.object_type]
                    for oi in ois:
                        if not pd.isna(oi):
                            marking.add_token(pl, oi)
                break
    return marking


def new_compute_marking(ocel: OCEL, ocpn: ObjectCentricPetriNet):
    df = succint_mdl_to_exploded_mdl(ocel.log.log)
    marking = Marking()
    for persp in ocpn.object_types:
        net, im, fm = ocpn.nets[persp]
        log = project_log(df, persp)
        replay_results = run_timed_replay(log, net, im, fm)
        for result in replay_results:
            token_id = result['trace_id']
            reached_marking = result['reached_marking']
            for p in reached_marking.items():
                for i in range(p[1]):
                    marking.add_token(ocpn.find_place(p[0].name), token_id)
    return marking


def FPI(aim: ActionInterfaceModel, change: ActionChange, tw: Tuple[datetime.datetime, datetime.datetime], ocel: OCEL, measure, agg, ot=None) -> FunctionWisePerformanceImpact:
    change_log = time_filtering.events(ocel, change.tw[0], change.tw[1])
    comp_log = time_filtering.events(ocel, tw[0], tw[1])
    perf_diff_dict = {}
    for t in change.transitions:
        try:
            perf_parameters = {'measure': measure,
                               'activity': t.name, 'aggregation': agg, 'object_type': ot}
            change_metric = performance_factory.apply(
                change_log, variant='event_object_graph_based', parameters=perf_parameters)
            comp_metric = performance_factory.apply(
                comp_log, variant='event_object_graph_based', parameters=perf_parameters)
            perf_diff_dict[t] = change_metric - comp_metric
        except:
            perf_diff_dict[t] = None
    return perf_diff_dict


def OPI(aim: ActionInterfaceModel, change: ActionChange, tw: Tuple[datetime.datetime, datetime.datetime], ocel: OCEL, measure, agg, ot) -> ObjectWisePerformanceImpact:
    change_log = time_filtering.events(ocel, change.tw[0], change.tw[1])
    comp_log = time_filtering.events(ocel, tw[0], tw[1])
    perf_diff_dict = {}
    for t in change.transitions:
        try:
            perf_parameters = {'measure': measure,
                               'activity': t.name, 'aggregation': agg, 'object_type': ot}
            change_metric = performance_factory.apply(
                change_log, variant='event_object_graph_based', parameters=perf_parameters)
            comp_metric = performance_factory.apply(
                comp_log, variant='event_object_graph_based', parameters=perf_parameters)
            perf_diff_dict[t] = change_metric - comp_metric
        except:
            perf_diff_dict[t] = None
    return perf_diff_dict
