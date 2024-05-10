from multiset import *
import networkx as nx
import copy
import itertools

def abstract_ocpn_to_DG(ocpn):
    DG = nx.DiGraph()
    nodes = set()
    silence_transitions = [tr for tr in ocpn.transitions if tr.silent]
    for tr in silence_transitions:       
        endpoints_start = [arc.source for arc in tr.in_arcs]
        endpoints_end = [arc.target for arc in tr.out_arcs]
        grouped_start = {key: list(group) for key, group in itertools.groupby(endpoints_start, key=lambda obj: obj.object_type)}
        grouped_end = {key: list(group) for key, group in itertools.groupby(endpoints_end, key=lambda obj: obj.object_type)}
        for ot1,start in grouped_start.items():
            for ot2,end in grouped_end.items():
                if ot2 == ot1:
                    nodes_start = [ele.name for ele in start]
                    nodes_end = [ele.name for ele in end]
                    edges=list(itertools.product(nodes_start,nodes_end))
                    for ed in edges:
                        for i in {0,1}:
                            if ed[i] not in nodes:
                                nodes.add(ed[i])
                                DG.add_node(ed[i])
                        DG.add_edge(ed[0],ed[1],label=tr.label)
    return DG


def find_path(DG,start,end):
    if start not in list(DG.nodes) or end not in list(DG.nodes):
        return None
    try:        
        return nx.shortest_simple_paths(DG,start,end)
    except nx.NetworkXNoPath:
        return None


def verify(dg,marking,path,obj,parameters):
    marking_copy = {}
    for key,value in marking.items():
        marking_copy[key]=copy.deepcopy(value)    
    transition_dict = parameters['transition_dict']
    enabled = True
    unenabled_edge = None
    for i in range(len(path[:-1])):
        for u, v, data in dg.edges(data=True):
            if u == path[i] and v == path[i+1]:
                tr_name = data.get("label")
                break
        curr_tr = transition_dict[tr_name]
        preset = [(arc.source,arc.weight) for arc in curr_tr.in_arcs if arc.source.object_type==obj[0]]
        postset = [(arc.target,arc.weight) for arc in curr_tr.out_arcs if arc.target.object_type==obj[0]]  
        if any([len([o for o in marking_copy[p] if o==obj])<w for (p,w) in preset]):    
            enabled = False
            unenabled_edge = (path[i],path[i+1])
            return enabled, unenabled_edge
        else:
            for (pl,w) in preset:
                marking_copy[pl].remove(obj,multiplicity=w)
            for (pl,w) in postset:
                marking_copy[pl].add(obj,multiplicity=w)
    return enabled, unenabled_edge


def find_shortest_executable_path(marking,dg,obj,paths_list,index,parameters,information):    
    if paths_list == None or index >= len(paths_list):
        return None,information
    verification,_ = verify(dg,marking,paths_list[index],obj,parameters)
    information['number_of_verified_paths'] += 1
    information['length_of_verified_paths'].append(len(paths_list[index]))
    if verification:
        return paths_list[index],information
    else:    
        return find_shortest_executable_path(marking,dg,obj,paths_list,index+1,parameters,information)