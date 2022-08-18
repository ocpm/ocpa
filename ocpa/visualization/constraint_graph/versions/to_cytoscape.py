
def apply(pattern_garph, parameters=None):
    if parameters is None:
        parameters = {}
    nodes = set()
    cy_edges = []
    cy_nodes = []
    for elem in pattern_garph.cf_edges:
        source, target = elem.source.name, elem.target.name
        if source not in nodes:
            nodes.add(source)
            cy_nodes.append(
                {"data": {"id": source, "label": source}, "classes": 'activity'})
        if target not in nodes:
            nodes.add(target)
            cy_nodes.append(
                {"data": {"id": target, "label": target}, "classes": 'activity'})
        if elem.label == 'skip':
            cy_edges.append(
                {"data": {"source": source, "target": target, "label": f'{elem.label} \n {elem.object_type},{elem.threshold}'}, "classes": 'loop'})
        else:
            cy_edges.append(
                {"data": {"source": source, "target": target, "label": f'{elem.label} \n {elem.object_type},{elem.threshold}'}})

    for elem in pattern_garph.obj_edges:
        source, target = elem.source.name, elem.target.name
        if source not in nodes:
            nodes.add(source)
            cy_nodes.append(
                {"data": {"id": source, "label": source}, "classes": 'object_type'})
        if target not in nodes:
            nodes.add(target)
            cy_nodes.append(
                {"data": {"id": target, "label": target}, "classes": 'activity'})
        cy_edges.append(
            {"data": {"source": source, "target": target, "label": f'{elem.label} \n {elem.threshold}'}})

    for elem in pattern_garph.perf_edges:
        formula_node = elem.source
        if formula_node.agg is not None and formula_node.object_type is not None:
            source = f"{formula_node.agg} {formula_node.diag} {formula_node.object_type} {formula_node.comparator} {formula_node.threshold}"
        elif formula_node.agg is None and formula_node.object_type is not None:
            source = f"{formula_node.diag} {formula_node.object_type} {formula_node.comparator} {formula_node.threshold}"
        elif formula_node.agg is not None and formula_node.object_type is None:
            source = f"{formula_node.agg} {formula_node.diag} {formula_node.comparator} {formula_node.threshold}"
        else:
            raise ValueError(
                f'Provide 1) diagnostics, 2) comparators, 3) threshold')
        target = elem.target.name
        if source not in nodes:
            nodes.add(source)
            cy_nodes.append(
                {"data": {"id": source, "label": source}, "classes": 'formula'})
        if target not in nodes:
            nodes.add(target)
            cy_nodes.append(
                {"data": {"id": target, "label": target}, "classes": 'activity'})
        cy_edges.append(
            {"data": {"source": source, "target": target}})
    elements = cy_nodes + cy_edges
    return cy_nodes, cy_edges
