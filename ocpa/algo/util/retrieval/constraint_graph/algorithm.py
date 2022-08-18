from ocpa.objects.graph.constraint_graph.obj import ConstraintGraph, ActivityNode, ObjectTypeNode, FormulaNode, ControlFlowEdge, ObjectRelationEdge, PerformanceEdge


def apply(pattern_graph_elements):
    pg = ConstraintGraph(pattern_graph_elements['name'])
    for elem in pattern_graph_elements['cf_edges']:
        source, target = ActivityNode(
            elem['source']), ActivityNode(elem['target'])
        label = elem['label']
        objec_type = elem['object_type']
        threshold = elem['threshold']
        if source not in pg.nodes:
            pg.add_node(source)
        if target not in pg.nodes:
            pg.add_node(target)
        pg.add_cf_edge(ControlFlowEdge(
            source, target, label, objec_type, threshold))

    for elem in pattern_graph_elements['or_edges']:
        source, target = ObjectTypeNode(
            elem['source']), ActivityNode(elem['target'])
        label = elem['label']
        threshold = elem['threshold']
        if source not in pg.nodes:
            pg.add_node(source)
        if target not in pg.nodes:
            pg.add_node(target)
        pg.add_obj_edge(ObjectRelationEdge(source, target, label, threshold))

    for elem in pattern_graph_elements['perf_edges']:
        if elem['formula_agg'] is not None and elem['formula_obj'] is not None:
            source = FormulaNode(diag=elem['formula_diag'], comparator=elem['formula_comp'], threshold=float(
                elem['formula_thre']), agg=elem['formula_agg'], object_type=elem['formula_obj'])
        elif elem['formula_agg'] is None and elem['formula_obj'] is not None:
            source = FormulaNode(diag=elem['formula_diag'], comparator=elem['formula_comp'], threshold=float(
                elem['formula_thre']), object_type=elem['formula_obj'])
        elif elem['formula_agg'] is not None and elem['formula_obj'] is None:
            source = FormulaNode(diag=elem['formula_diag'], comparator=elem['formula_comp'], threshold=float(
                elem['formula_thre']), agg=elem['formula_agg'])
        target = ActivityNode(elem['target'])
        if source not in pg.nodes:
            pg.add_node(source)
        if target not in pg.nodes:
            pg.add_node(target)
        pg.add_perf_edge(PerformanceEdge(source, target))
    return pg
