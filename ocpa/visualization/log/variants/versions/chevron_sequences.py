import networkx as nx

def event_to_x(graph, event):
    pre = list(graph.predecessors(event))
    if len(pre) == 0:
        return 0
    else:
        return max([event_to_x(graph, pre_e) for pre_e in pre]) + 1


def event_to_y(graph, event, y_mappings):
    in_edges = graph.in_edges(event)
    out_edges = graph.out_edges(event)
    objects = []
    for e in in_edges:
        object_strings = [s.strip() for s in graph.edges[e]["label"].split(":")]
        for o in object_strings:
            objects+=[o]
            #o_tuple =o.replace('(','').replace(')','').split(",")
            #if o_tuple[0] not in objects.keys:
            #    objects[o_tuple[0]] = [o_tuple[1]]
            #else:
            #    objects[o_tuple[0]] += [o_tuple[1]]
    for e in out_edges:
        object_strings = [s.strip() for s in graph.edges[e]["label"].split(":")]
        for o in object_strings:
            objects += [o]
    return [y_mappings[o] for o in set(objects)]

def graph_to_2d(ocel,graph):
    all_obs = {}
    mapping_activity = dict(zip(ocel.log["event_id"], ocel.log["event_activity"]))
    for event in graph.nodes:
        in_edges = graph.in_edges(event)
        out_edges = graph.out_edges(event)
        for e in in_edges:
            object_strings = [s.strip() for s in graph.edges[e]["label"].split(":")]
            for o in object_strings:
                o_tuple =o.replace('(','').replace(')','').split(",")
                if o_tuple[0] not in all_obs.keys():
                    all_obs[o_tuple[0]] = [o]
                elif o not in all_obs[o_tuple[0]]:
                    all_obs[o_tuple[0]] += [o]
        for e in out_edges:
            object_strings = [s.strip() for s in graph.edges[e]["label"].split(":")]
            for o in object_strings:
                o_tuple =o.replace('(','').replace(')','').split(",")
                if o_tuple[0] not in all_obs.keys():
                    all_obs[o_tuple[0]] = [o]
                elif o not in all_obs[o_tuple[0]]:
                    all_obs[o_tuple[0]] += [o]
    y_mappings = {}
    lane_info = {}
    y = 0
    for ot in all_obs.keys():
        ot_o = 1
        for o in all_obs[ot]:
            y_mappings[o] = y
            lane_info[y] = ot+"_"+str(ot_o)
            y+=1
            ot_o += 1
    coords = {}
    for event in graph.nodes:
        x = event_to_x(graph, event)
        y = event_to_y(graph,event, y_mappings)
        coords[event] = (x,y)
    #coords = list(coords.items())
    coords = [[k,v] for k,v in coords.items()]
    for i in range(0,len(coords)):
        coords[i][0] = mapping_activity[coords[i][0]]
    return (coords, lane_info)


def apply(obj, parameters=None):
    variant_layouting = {}
    for v,v_graph in obj.variant_graphs.items():
        variant_layouting[v] = graph_to_2d(obj,v_graph)
    return variant_layouting