import networkx as nx


def eog_from_log(table_log):
    ocel = table_log.log.copy()
    EOG = nx.DiGraph()
    EOG.add_nodes_from(ocel["event_id"].to_list())
    edge_list = []

    ot_index = {ot: list(ocel.columns.values).index(ot)
                for ot in table_log.object_types}
    event_index = list(ocel.columns.values).index("event_id")
    arr = ocel.to_numpy()
    last_ev = {}
    for i in range(0, len(arr)):
        for ot in table_log.object_types:
            for o in arr[i][ot_index[ot]]:
                if (ot, o) in last_ev.keys():
                    edge_source = arr[last_ev[(ot, o)]][event_index]
                    edge_target = arr[i][event_index]
                    edge_list += [(edge_source, edge_target)]
                last_ev[(ot, o)] = i
    EOG.add_edges_from(edge_list)
    return EOG
