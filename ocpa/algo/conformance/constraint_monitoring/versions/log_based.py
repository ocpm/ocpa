from ocpa.objects.graph.constraint_graph.obj import ConstraintGraph
from ocpa.objects.log.variants.obj import ObjectCentricEventLog
from ocpa.objects.log.ocel import OCEL
from typing import List, Dict


def apply(pg: ConstraintGraph, ocel: OCEL, diag: Dict, parameters=None) -> List[str]:
    evals = []
    for cf_edge in pg.cf_edges:
        evals.append(evaluate_cf_edge(ocel.obj, cf_edge))

    for obj_edge in pg.obj_edges:
        evals.append(evaluate_or_edge(ocel.obj, obj_edge))

    for perf_edge in pg.perf_edges:
        evals.append(evaluate_perf_edge(diag, perf_edge))
    if all(eval == False for eval in evals):
        return False, ""
    else:
        return True, [eval for eval in evals if eval != False]


def evaluate_cf_edge(ocel, cf_edge):
    if cf_edge.label == 'causal':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        strength = ocel.causal_relation(
            cf_edge.object_type, source_act, target_act)
        if strength > cf_edge.threshold:
            output = cf_edge.message(strength)
            # print(output)
            return output
        else:
            return False

    elif cf_edge.label == 'concur':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        strength = ocel.concur_relation(
            cf_edge.object_type, source_act, target_act)
        if strength > cf_edge.threshold:
            output = cf_edge.message(strength)
            # print(output)
            return output
        else:
            return False

    elif cf_edge.label == 'choice':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        strength = ocel.choice_relation(
            cf_edge.object_type, source_act, target_act)
        if strength > cf_edge.threshold:
            output = cf_edge.message(strength)
            # print(output)
            return output
        else:
            return False

    elif cf_edge.label == 'skip':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        if source_act != target_act:
            return False
        ot = cf_edge.object_type
        strength = 1 - \
            ocel.num_ot_objects_containing_acts(
                ot, [source_act])/len(ocel.ot_objects(ot))
        if strength > cf_edge.threshold:
            output = cf_edge.message(strength)
            # print(output)
            return output
        else:
            return False


def evaluate_or_edge(ocel, obj_edge):
    ot = obj_edge.source.name
    act = obj_edge.target.name
    if obj_edge.label == 'absent':
        strength = ocel.absent_involvement(ot, act)
        if strength > obj_edge.threshold:
            output = obj_edge.message(strength)
            # print(output)
            return output
    elif obj_edge.label == 'present':
        strength = 1 - ocel.absent_involvement(ot, act)
        if strength > obj_edge.threshold:
            output = obj_edge.message(strength)
            # print(output)
            return output
    elif obj_edge.label == 'singular':
        strength = ocel.singular_involvement(ot, act)
        if strength > obj_edge.threshold:
            output = obj_edge.message(strength)
            # print(output)
            return output
    elif obj_edge.label == 'multiple':
        strength = ocel.multiple_involvement(ot, act)
        if strength > obj_edge.threshold:
            output = obj_edge.message(strength)
            # print(output)
            return output
    return False


def evaluate_perf_edge(diag, perf_edge):
    formula_node = perf_edge.source
    act_node = perf_edge.target
    act_name = act_node.name
    print(formula_node.diag, formula_node.comparator, formula_node.threshold)
    if act_name in diag:
        if formula_node.diag in diag[act_name]:
            if formula_node.object_type is not None:
                if formula_node.agg is not None:
                    val = diag[act_name][formula_node.diag][formula_node.object_type][formula_node.agg]
                else:
                    val = diag[act_name][formula_node.diag][formula_node.object_type]
            else:
                if formula_node.agg is not None:
                    val = diag[act_name][formula_node.diag][formula_node.agg]
                else:
                    val = diag[act_name][formula_node.diag]
        else:
            return False
    else:
        return False
    if formula_node.comparator == '<':
        if val < formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    elif formula_node.comparator == '>':
        if val > formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    elif formula_node.comparator == '<=':
        if val >= formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    elif formula_node.comparator == '>=':
        if val >= formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    elif formula_node.comparator == '!=':
        if val != formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    elif formula_node.comparator == '=':
        if val == formula_node.threshold:
            print(perf_edge.message)
            return perf_edge.message
    else:
        raise ValueError(f'{formula_node.comparator} is not defined.')
    return False
