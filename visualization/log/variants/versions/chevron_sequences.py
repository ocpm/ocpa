import time

import networkx as nx

def event_to_x(graph, event, cache_map):
    pre = list(graph.predecessors(event))
    if len(pre) == 0:
        return 0
    else:
        return max([event_to_x(graph, pre_e, cache_map) if pre_e not in cache_map.keys() else cache_map[pre_e] for pre_e in pre]) + 1

def event_to_x_end(graph, event, coords):
    suc = list(graph.successors(event))
    if len(suc) == 0:
        return coords[event][0]
    else:
        return min([coords[suc_e][0] for suc_e in suc]) - 1


def event_to_y(graph, event, y_mappings, ocel):
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
    for ot_ in ocel.object_types:
        ot = "'" + ot_ + "'"
        for o in ocel.log.log.loc[event][ot_]:
            o = "(" + ot + ", '" + o + "')"
            objects += [o]
    return [y_mappings[o] for o in set(objects) if o in y_mappings.keys()]

def graph_to_2d(ocel,graph_obj,mapping_activity):
    all_obs = {}
    graph = graph_obj[0]
    relevant_obs = graph_obj[1]
    s_time = time.time()
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

        for ot_ in ocel.object_types:
            ot = "'" + ot_ + "'"
            for o in ocel.log.log.loc[event][ot_]:
                o = "("+ot+", '"+o+"')"
                if ot not in all_obs.keys():
                    all_obs[ot] = [o]
                elif o not in all_obs[ot]:
                    all_obs[ot] += [o]

    y_mappings = {}
    lane_info = {}
    y = 0

    rel_obs_dict = {}
    for ob in relevant_obs:
        ot_string = "'" + ob[0] + "'"
        ob_string = "("+ot_string+", '"+ob[1]+"')"
        if ot_string not in rel_obs_dict.keys():
            rel_obs_dict[ot_string] = []
        rel_obs_dict[ot_string].append(ob_string)
    #intersection between relevant objects and all
    for ot in all_obs.keys():
        to_remove = []
        for o in all_obs[ot]:
            if ot not in rel_obs_dict.keys():
                to_remove.append(o)
            elif o not in rel_obs_dict[ot]:
                to_remove.append(o)
        all_obs[ot] = [e for e in all_obs[ot] if e not in to_remove]
    for ot in sorted(list(all_obs.keys())):
        ot_o = 1
        for o in all_obs[ot]:
            y_mappings[o] = y
            lane_info[y] = (str(ot).replace("'",""),str(ot).replace("'","")+'_'+str(ot_o))
            y+=1
            ot_o += 1
    #print("Before " + str(time.time() - s_time))
    s_time = time.time()
    coords = {}
    coords_tmp = {}
    x_starter = 0
    cache_map = {}
    for event in sorted(list(graph.nodes)):
        ss_time= time.time()
        x_start = event_to_x(graph, event, cache_map)
        cache_map[event] = x_start
        x_starter += time.time() -ss_time
        y = event_to_y(graph,event, y_mappings, ocel)
        coords_tmp[event] = [x_start,y]
    #print("Only start "+ str(x_starter))
    #print("x start "+str(time.time()-s_time))
    s_time=time.time()
    for event in graph.nodes:
        x_end = event_to_x_end(graph, event, coords_tmp)
        coords[event] = [[coords_tmp[event][0],x_end], coords_tmp[event][1]]
    #print("x end " + str(time.time() - s_time))
    s_time= time.time()
    #coords = list(coords.items())
    coords = [[k,v] for k,v in coords.items()]
    for i in range(0,len(coords)):
        coords[i][0] = mapping_activity[coords[i][0]]
    #print(coords)
    #print("After "+str(time.time()-s_time))
    return (coords, lane_info)


def apply(obj, parameters=None):
    if "measure" in parameters.keys():
        return apply_measuring(obj,parameters)
    else:
        variant_layouting = {}
        mapping_activity = dict(zip(obj.log.log["event_id"], obj.log.log["event_activity"]))
        c= 0
        for v,v_graph in obj.variant_graphs.items():
            #print("Next "+str(c))
            c+=1
            #print(len(list(v_graph.nodes)))
            variant_layouting[v] = graph_to_2d(obj,v_graph,mapping_activity)
        return variant_layouting

######only for experiments
def apply_measuring(obj, parameters={}):
    runtimes = []
    variant_layouting = {}
    mapping_activity = dict(zip(obj.log["event_id"], obj.log["event_activity"]))
    c= 0
    for v,v_graph in obj.variant_graphs.items():
        c+=1
        #print(len(list(v_graph.nodes)))
        s_time = time.time()
        variant_layouting[v] = graph_to_2d(obj,v_graph,mapping_activity)
        #print("Done " + str(c))
        runtimes.append((len(list(v_graph[0].nodes)),len(list(v_graph[1])),time.time()-s_time))
       # print("fonex " + str(c))
    return  runtimes