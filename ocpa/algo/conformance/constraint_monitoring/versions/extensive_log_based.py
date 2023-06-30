from ocpa.objects.graph.extensive_constraint_graph.obj import ExtensiveConstraintGraph
from ocpa.objects.log.ocel import OCEL
from typing import List, Dict
from ocpa.algo.enhancement.event_graph_based_performance import algorithm as performance_factory
from ocpa.util.util import AGG_MAP
import logging

logging.basicConfig(level=logging.INFO)


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
    
def calculate_metric(quantity: int, total: int):
    if total > 0:
        return quantity/total
    else:
        return 0


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
    op = oa_edge.operator
    threshold = oa_edge.threshold
    act = oa_edge.target.name
    label = oa_edge.label.split("-")
    if len(label) == 1:
        label = label[0]
        if label == 'exist':
            metric = calculate_metric(len(ocel.obj.existence(ot, act)), len(ocel.obj.ot_objects[ot]))

        elif label == 'absent':
            metric = calculate_metric(len(ocel.obj.object_absence(ot, act)), len(ocel.obj.act_events[act]))

        elif label == 'singular':
            metric = calculate_metric(len(ocel.obj.object_singular(ot, act)), len(ocel.obj.act_events[act]))

        elif label == 'multiple':
            metric = calculate_metric(len(ocel.obj.object_multiple(ot, act)), len(ocel.obj.act_events[act]))

        elif label == 'present':
            metric = calculate_metric(len(ocel.obj.object_singular(ot, act))+len(ocel.obj.object_multiple(ot, act)), len(ocel.obj.act_events[act]))
        else:
            logging.error(f'Error in evaluating {oa_edge}: {label} is not defined. Returning False by default.')
    elif len(label) == 2:
        agg = label[0]
        label = label[1]
        if agg not in AGG_MAP:
            logging.error(f'Error in evaluating {oa_edge}: {agg} is not defined. Returning False by default.')
            return False
        if label not in ['pooling', 'lagging', 'rediness', 'obj_freq', 'act_freq']:
            logging.error(f'Error in evaluating {oa_edge}: {label} is not defined. Returning False by default.')
            return False
        else:
            perf_parameters = {'measure': label,
                            'activity': act, 'aggregation': agg, 'object_type': ot}
            metric = performance_factory.apply(
                ocel, variant='event_object_graph_based', parameters=perf_parameters)
    else:
        logging.error(f'Error in evaluating {oa_edge}: {label} is not defined. Returning False by default.')
        return False

    logging.info(f'Evaluating {label} for ({ot, act}): {metric}, {op}, {threshold}')
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
        logging.error(f'Error in evaluating {aa_edge}: {label} is not defined. Returning False by default.')
        return False
    elif len(label) == 2:
        agg = label[0]
        label = label[1]
        if agg not in AGG_MAP:
            logging.error(f'Error in evaluating {aa_edge}: {agg} is not defined. Returning False by default.')
            return False
        if label not in ['flow', 'sojourn', 'sync']:
            logging.error(f'Error in evaluating {aa_edge}: {label} is not defined. Returning False by default.')
            return False
        else:
            perf_parameters = {'measure': label,
                            'activity': act, 'aggregation': agg}
            metric = performance_factory.apply(
                ocel, variant='event_object_graph_based', parameters=perf_parameters)
    else:
        logging.error(f'Error in evaluating {aa_edge}: {label} is not defined. Returning False by default.')
        return False
    
    logging.info(f'Evaluating {label} for {act}: {metric}, {op}, {threshold}')
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
    
    if label == 'coexist':
        metric = calculate_metric(len(ocel.obj.coexistence(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'exclusive':
        metric = calculate_metric(len(ocel.obj.exclusiveness(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'choice':
        metric = calculate_metric(len(ocel.obj.choice(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'xorChoice':
        metric = calculate_metric(len(ocel.obj.xor_choice(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'cause':
        metric = calculate_metric(len(ocel.obj.followed_by(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'directlyCause':
        metric = calculate_metric(len(ocel.obj.directly_followed_by(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'precede':
        metric = calculate_metric(len(ocel.obj.precedence(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))

    elif label == 'block':
        metric = calculate_metric(len(ocel.obj.block(ot, act1, act2)), len(ocel.obj.ot_objects[ot]))
    else:
        logging.error(f'Error in evaluating {aoa_edge}: {label} is not defined. Returning False by default.')
        return False
    
    logging.info(f'Evaluating {label} for ({act1, ot, act2}): {metric}, {op}, {threshold}')
    if compare(metric, op, threshold):
        return True
    else:
        return False
