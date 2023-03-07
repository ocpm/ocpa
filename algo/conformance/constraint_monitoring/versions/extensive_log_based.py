from ocpa.objects.graph.extensive_constraint_graph.obj import ExtensiveConstraintGraph
from ocpa.objects.log.ocel import OCEL
from typing import List, Dict
from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory
from ocpa.algo.util.util import AGG_MAP


def apply(pg: ExtensiveConstraintGraph, ocel: OCEL, parameters=None) -> List[str]:
    evals = []
    for oa_edge in pg.oa_edges:
        evals.append(evaluate_oa_edge(ocel, oa_edge))

    for aa_edge in pg.aa_edges:
        evals.append(evaluate_aa_edge(ocel, aa_edge))

    for aoa_edge in pg.aoa_edges:
        evals.append(evaluate_aoa_edge(ocel, aoa_edge))
    if all(eval == False for eval in evals):
        return False, ""
    else:
        return True, [eval for eval in evals if eval != False]


def compare(a, op, b):
    if op == '<':
        if a < b:
            return True
    elif op == '>':
        if a > b:
            return True
    elif op == '<=':
        if a >= b:
            return True
    elif op == '>=':
        if a >= b:
            return True
    elif op == '!=':
        if a != b:
            return True
    elif op == '=':
        if a == b:
            return True
    else:
        raise ValueError(f'{op} is not defined.')


def evaluate_oa_edge(ocel, oa_edge):
    ot = oa_edge.source.name
    act = oa_edge.target.name
    label = oa_edge.label.split("-")
    if len(label) == 1:
        label = label[0]
    elif len(label) == 2:
        agg = label[0]
        if agg not in AGG_MAP:
            raise ValueError(f'Aggregation {agg} is not supported')
        label = label[1]
    else:
        raise ValueError("Invalid label for the constraint graph edge")
    op = oa_edge.operator
    threshold = oa_edge.threshold
    if label == 'exist':
        metric = ocel.obj.existence_metric(ot, act)

    elif label == 'non-exist':
        metric = ocel.obj.non_existence_metric(ot, act)

    elif label == 'absent':
        metric = ocel.obj.object_absence_metric(ot, act)

    elif label == 'singular':
        metric = ocel.obj.object_singular_metric(ot, act)

    elif label == 'multiple':
        metric = ocel.obj.object_multiple_metric(ot, act)

    elif label == 'present':
        metric = ocel.obj.object_presence_metric(ot, act)

    elif label in ['pooling', 'lagging', 'readying']:
        perf_parameters = {'measure': label,
                           'activity': act, 'aggregation': agg}
        metric = performance_factory.apply(
            ocel, variant='event_object_graph_based', parameters=perf_parameters)

    if compare(metric, op, threshold):
        return True
    else:
        return False


def evaluate_aa_edge(ocel, aa_edge):
    act = aa_edge.source.name
    op = aa_edge.operator
    threshold = aa_edge.threshold
    label = aa_edge.label.split("-")
    if len(label) == 1:
        label = label[0]
    elif len(label) == 2:
        agg = label[0]
        if agg not in AGG_MAP:
            raise ValueError(f'Aggregation {agg} is not supported')
        label = label[1]
    else:
        raise ValueError("Invalid label for the constraint graph edge")
    if label in ['flow', 'sojourn', 'sync']:
        perf_parameters = {'measure': label,
                           'activity': act, 'aggregation': agg}
        metric = performance_factory.apply(
            ocel, variant='event_object_graph_based', parameters=perf_parameters)

    if compare(metric, op, threshold):
        return True
    else:
        return False


def evaluate_aoa_edge(ocel, aoa_edge):
    act1 = aoa_edge.source.name
    ot = aoa_edge.inner.name
    act2 = aoa_edge.target.name
    label = aoa_edge.label
    op = aoa_edge.operator
    threshold = aoa_edge.threshold
    if label == 'co-exist':
        metric = ocel.obj.coexistence_metric(ot, act1, act2)

    elif label == 'exclusive':
        metric = ocel.obj.exclusiveness_metric(ot, act1, act2)

    elif label == 'choice':
        metric = ocel.obj.choice_metric(ot, act1, act2)

    elif label == 'xor-choice':
        metric = ocel.obj.xor_choice_metric(ot, act1, act2)

    elif label == 'followed_by':
        metric = ocel.obj.followed_by_metric(ot, act1, act2)

    elif label == 'directly_followed_by':
        metric = ocel.obj.directly_followed_by_metric(ot, act1, act2)

    elif label == 'precede':
        metric = ocel.obj.precedence_metric(ot, act1, act2)

    elif label == 'block':
        metric = ocel.obj.block_metric(ot, act1, act2)

    if compare(metric, op, threshold):
        return True
    else:
        return False
