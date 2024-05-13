from multiset import *
import networkx as nx

'''
Freeze all tokens that conflict with the introduced token
'''
def solve_token_flooding(marking,place,object,method='S_component',parameters=None):
    f=0
    frozen_tokens = Multiset()  
    if method == 'boundness':       
        if object in marking[place]:
            marking[place].remove(object,multiplicity=1)
            frozen_tokens.add((place.name,object[1]))
            f += 1
    elif method == 'S_component':
        S_component = parameters['S_component']
        for circle in S_component:
            if place in circle:
                for pl in set(circle):
                    if object in marking[pl]:
                        marking[pl].remove(object,multiplicity=1)
                        frozen_tokens.add((pl.name,object[1]))
                        f += 1
    return f,frozen_tokens

def calculate_S_component(ocpn):
    G = nx.DiGraph()
    G.add_nodes_from(ocpn.places)
    connection = set()
    parallel_places = []
    for tr in ocpn.transitions:
        for ot in ocpn.object_types:
            preset = [arc.source for arc in tr.in_arcs if arc.source.object_type==ot]
            postset = [arc.target for arc in tr.out_arcs if arc.target.object_type==ot]
            if len(preset)>1:
                parallel_places.append(preset)
            if len(postset)>1:
                parallel_places.append(postset)
    for tr in ocpn.transitions:
        for arc1 in tr.in_arcs:
            for arc2 in tr.out_arcs:
                if arc1.source.object_type == arc2.target.object_type:
                    connection.add((arc1.source,arc2.target))
    G.add_edges_from(connection)
    try:
        loops = list(nx.simple_cycles(G))
    except:
        loops = []
    is_finished = False
    while not is_finished:
        is_finished = True
        for l1 in loops:
            for l2 in loops:
                if len(set(l1)&set(l2))>0 and not l1==l2 and l1[0].object_type == l2[0].object_type:
                    merged_circle = set(l1)|set(l2)
                    if all([len(set(parallel)&merged_circle)<2 for parallel in parallel_places]):
                        loops.remove(l1)
                        loops.remove(l2)
                        loops.append(list(merged_circle ))
                        is_finished = False
                        break
            if not is_finished:
                break
    return loops