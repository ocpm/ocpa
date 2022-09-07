def project_subgraph_on_activity(ocel, v_g, case_id, mapping_objects, mapping_activity):
    v_g_ = v_g.copy()
    for node in v_g.nodes():
        if not set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id]):
            v_g_.remove_node(node)
            continue
        v_g_.nodes[node]['label'] = mapping_activity[node] + ": ".join(
            [e[0] for e in sorted(list(set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id])))])
    for edge in v_g.edges():
        source, target = edge
        if not set(mapping_objects[source]) & set(mapping_objects[target]) & set(ocel.process_execution_objects[case_id]):
            v_g_.remove_edge(source, target)
            continue
        v_g_.edges[edge]['type'] = ": ".join(
            [e[0] for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(
                ocel.process_execution_objects[case_id])))])
        v_g_.edges[edge]['label'] = ": ".join(
            [str(e) for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(
                ocel.process_execution_objects[case_id])))])
    return v_g_