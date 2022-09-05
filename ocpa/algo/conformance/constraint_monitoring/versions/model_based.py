from ocpa.objects.graph.constraint_graph.obj import ConstraintGraph
from ocpa.objects.oc_petri_net.obj import EnhancedObjectCentricPetriNet
from typing import List


def apply(pg: ConstraintGraph, eocpn: EnhancedObjectCentricPetriNet, parameters=None) -> List[str]:
    evals = []
    for cf_edge in pg.cf_edges:
        evals.append(evaluate_cf_edge(eocpn, cf_edge))

    for obj_edge in pg.obj_edges:
        evals.append(evaluate_or_edge(eocpn, obj_edge))

    for perf_edge in pg.perf_edges:
        evals.append(evaluate_perf_edge(eocpn, perf_edge))
    if all(eval == False for eval in evals):
        return False, ""
    else:
        return True, [eval for eval in evals if eval != False]


def evaluate_cf_edge(eocpn, cf_edge):
    if cf_edge.label == 'causal':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        exist = True
        for bv in eocpn.behavior:
            if source_act in bv and target_act in bv:
                source_index = bv.index(source_act)
                target_index = bv.index(target_act)
            else:
                return False
            if source_index < target_index:
                continue
            else:
                return False
        if exist:
            print(cf_edge.message)
            return cf_edge.message

    elif cf_edge.label == 'concur':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        exist = True
        for bv in eocpn.behavior:
            if source_act in bv and target_act in bv:
                bv_source_index = bv.index(source_act)
                bv_target_index = bv.index(target_act)
            else:
                continue
            if bv_source_index > bv_target_index:
                for bv2 in eocpn.behavior:
                    if source_act in bv2 and target_act in bv2:
                        bv2_source_index = bv2.index(source_act)
                        bv2_target_index = bv2.index(target_act)
                    else:
                        continue
                    if bv2_source_index < bv2_target_index:
                        print(cf_edge.message)
                        return cf_edge.message
            else:
                continue
        return False

    elif cf_edge.label == 'choice':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        exist = True
        for bv in eocpn.behavior:
            if (source_act in bv or target_act in bv) and ~(source_act in bv and target_act in bv):
                continue
            else:
                return False
        if exist:
            print(cf_edge.message)
            return cf_edge.message

    elif cf_edge.label == 'skip':
        source_act = cf_edge.source.name
        target_act = cf_edge.target.name
        if source_act != target_act:
            return False
        exist = True
        for bv in eocpn.behavior:
            print(source_act, target_act, bv)
            if source_act in bv:
                for bv2 in eocpn.behavior:
                    if source_act not in bv2:
                        print(cf_edge.message)
                        return cf_edge.message
        return False


def evaluate_or_edge(eocpn, obj_edge):
    ot_node = obj_edge.source
    act_node = obj_edge.target
    tr = eocpn.ocpn.find_transition(act_node.name)
    if obj_edge.label == 'inc':
        if ot_node.name in tr.preset_object_type:
            print(obj_edge.message)
            return obj_edge.message
    elif obj_edge.label == 'exc':
        if ot_node.name not in tr.preset_object_type:
            print(obj_edge.message)
            return obj_edge.message
    elif obj_edge.label == 'var':
        for arc in tr.in_arcs:
            if arc.source.object_type == ot_node.name:
                if arc.variable == True:
                    print(obj_edge.message)
                    return obj_edge.message
    return False


def evaluate_perf_edge(eocpn, perf_edge):
    formula_node = perf_edge.source
    act_node = perf_edge.target
    act_name = act_node.name
    print(formula_node.diag, formula_node.comparator, formula_node.threshold)
    if act_name in eocpn.diagnostics:
        if formula_node.diag in eocpn.diagnostics[act_name]:
            if formula_node.object_type is not None:
                if formula_node.agg is not None:
                    val = eocpn.diagnostics[act_name][formula_node.diag][formula_node.object_type][formula_node.agg]
                else:
                    val = eocpn.diagnostics[act_name][formula_node.diag][formula_node.object_type]
            else:
                if formula_node.agg is not None:
                    val = eocpn.diagnostics[act_name][formula_node.diag][formula_node.agg]
                else:
                    val = eocpn.diagnostics[act_name][formula_node.diag]
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
