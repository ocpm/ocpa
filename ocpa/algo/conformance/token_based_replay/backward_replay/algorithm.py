import ocpa.algo.conformance.token_based_replay.backward_replay.variants.backward_searching_tree as backward_searching_tree
import ocpa.algo.conformance.token_based_replay.backward_replay.variants.shortest_path as shortest_path
from ocpa.objects.oc_petri_net import obj as obj_ocpa
from multiset import *
import time
import networkx as nx

def bst_backward_replay(element,marking,object,silence_constrain):
    information = {'missing_places':[],'time_coloring':0,'time_silence_execution':0,\
            'missing_objects':None,'silent_sequence':[]}
    '''
    BST initialization
    '''
    bst = backward_searching_tree.BackwardSearchingTree()
    if type(element)==obj_ocpa.ObjectCentricPetriNet.Place:
        '''
        Define dummy root
        '''
        final_place = element
        bst.root = bst.Operator(len(bst.operators),type='AND',label='dummy')
        node = bst.Node(len(bst.nodes),place=final_place,transition=None,end=True,weight=1)
        bst.connect_components(node,bst.root)
        bst.operators.add(bst.root)
        bst.nodes.add(node)
    elif type(element)==obj_ocpa.ObjectCentricPetriNet.Transition:
        transition = element
        bst.root = bst.Operator(len(bst.operators),type='AND',transition=transition)
        bst.operators.add(bst.root)
        preset = [(arc.source,arc.weight) for arc in transition.in_arcs if arc.source.object_type==object[0]]        
        for (pl,w) in preset:
            node = bst.Node(len(bst.nodes),place=pl,transition=None,end=True,weight=w)
            bst.nodes.add(node)
            bst.connect_components(node,bst.root)
    bst.constrains = backward_searching_tree.calculate_bst_constrain(bst,silence_constrain)
    '''
    Coloring and expansion
    '''
    while bst.root.color == 'yellow':
        for n in bst.extension_nodes:
            if object in marking[n.place] and not bst.is_place_occupied(n.place) and not n.place.final\
                and len([o for o in marking[n.place] if o==object])>=n.weight:
                n.color = 'green'
            elif n.label in n.parent.visit and not n.label is None:
                n.color = 'red'
            else:
                backward_searching_tree.extend_bst(bst,n)       
        time0 = time.time()
        bst.color_update()
        time1 = time.time()
        information['time_coloring'] += time1-time0
    '''
    Extraction and execution
    '''
    silence_sequence = bst.extract_silence_sequence()
    if silence_sequence == None:
        p,c = 0,0
    else:
        time0 = time.time()
        p,c = execute_silence_sequence(silence_sequence,marking,object)
        time1 = time.time()       
        information['time_silence_execution'] += time1-time0
    missing = [(p,w-len([o for o in marking[p] if o==object])) for (p,w) in bst.get_missing_nodes()]
    m = sum([weight for (_,weight) in missing])
    for (pl,weight) in missing:
        marking[pl].add(object,multiplicity=weight)

    information['missing_objects'] = Multiset({object[1]:len(missing)})
    information['missing_places'] = missing
    information['silent_sequence'].append(silence_sequence)
    
    return p,c,m,information

def cashed_bst_backward_replay(marking,obj,bst):
    information = {'missing_places':[],'time_coloring':0,'time_silence_execution':0,\
            'missing_objects':None,'silent_sequence':[]}
    for n in bst.nodes:
        if obj in marking[n.place] and not n.place.final and \
            len([o for o in marking[n.place] if o==obj])>=n.weight:
            n.color = 'green'
            n.end = True
        if n.end and n.color=='yellow':
            n.color = 'red'
    bst.color_update()
    silence_sequence = bst.extract_silence_sequence()
    silence_sequence = [silence for silence in silence_sequence if not silence is None]
    if silence_sequence == None or silence_sequence == []:
        p,c = 0,0
    else:
        p,c = execute_silence_sequence(silence_sequence,marking,obj)
        information['silent_sequence']=[obj,silence_sequence]
    missing = [(p,w-len([o for o in marking[p] if o==obj])) for (p,w) in bst.get_missing_nodes()]
    m = len(missing)
    for (pl,w) in missing:
        marking[pl].add(obj,multiplicity=w)
    information['missing_places'] = missing 
    information['missing_objects'] = Multiset({obj[1]:len(missing)})
    for n in bst.nodes|bst.operators:
        n.color = 'yellow'
        n.end = False
        if type(n)==backward_searching_tree.BackwardSearchingTree.Node and len(n.children) == 0:
            n.end = True    
    return p,c,m,information

def shortest_path_backward_replay(ocpn,dg,marking,obj,parameters):
    information = {'number_of_searched_pairs':0, 'number_of_verified_paths':0,'number_of_executable_paths':0,\
                   'length_of_verified_paths':[],'silent_sequence':[],'missing_places':[],'missing_objects':obj,\
                    'time_verify_path':0,'time_execute_silence':0,'time_find_path':0}
    preset = [ele[0] for ele in parameters['preset']]
    transition_dict = parameters['transition_dict']
    gamma_list = [pl.name for pl in preset if not obj in marking[pl] and pl.object_type==obj[0]]
    lambda_list = [pl.name for pl in ocpn.places-set(preset) if obj in marking[pl]]
    search_pairs = [(x,y) for x in lambda_list for y in gamma_list]
    found = True if len(gamma_list)==0 or len(lambda_list)==0 else False
    p,c,m,silence_sequence = 0,0,0,None
    while not found:
        information['number_of_searched_pairs'] += len(search_pairs)
        paths_verification=[]
        for pair in search_pairs:
            try:
                time0 = time.time()
                found_path = shortest_path.find_path(dg,pair[0],pair[1])
                time1 = time.time()
                information['time_find_path'] += time1-time0
                if found_path is None:
                    path_list = None
                else:
                    path_list = list(found_path)
                    paths_verification += path_list
            except nx.NetworkXNoPath:
                path_list = None       
        sorted_paths_verification = sorted(paths_verification,key=lambda path:len(path))
        found = True
        shortest_executable_path = None
        for places_path in sorted_paths_verification:
            time0 = time.time()
            verification,_ = shortest_path.verify(dg,marking,places_path,obj,parameters)
            time1 = time.time()
            information['time_verify_path'] += time1-time0
            information['length_of_verified_paths'].append(len(places_path))
            information['number_of_verified_paths'] += 1
            if verification:
                shortest_executable_path = places_path
                found = False
                break
        if found:
            break
        silence_sequence = []
        shortest_solution = shortest_executable_path
        for i in range(len(shortest_solution)-1):
            tr_name = dg.get_edge_data(shortest_solution[i],shortest_solution[i+1]).get('label')
            silence_sequence.append(transition_dict[tr_name])
        information['silent_sequence'] += silence_sequence
        time0 = time.time()
        p,c = execute_silence_sequence(silence_sequence,marking,obj)
        time1 = time.time()
        information['time_execute_silence'] += time1-time0
        information['number_of_executable_paths'] += 1
        gamma_list = [pl.name for pl in preset if not obj in marking[pl] and pl.object_type==obj[0]]
        lambda_list = [pl.name for pl in ocpn.places-set(preset) if obj in marking[pl]]
        search_pairs = [(x,y) for x in lambda_list for y in gamma_list]
        if len(gamma_list) == 0 or len(lambda_list) == 0:
            found = True
    information['missing_places'] = [(p,w-len([o for o in marking[p] if o==obj])) for (p,w) in parameters['preset'] if len([o for o in marking[p] if o==obj])<w]
    information['silent_sequence'] = [obj,information['silent_sequence']]
    information['missing_objects'] = Multiset({obj[1]:len(information['missing_places'])})
    for (pl,w) in parameters['preset']:
        #if not obj in marking[pl]:
        res_tokens = len([o for o in marking[pl] if o==obj])
        if res_tokens<w:
            m += w-res_tokens
            marking[pl].add(obj,multiplicity=w-res_tokens) 
    return p,c,m,information

def execute_silence_sequence(silence_sequence,marking,obj):
    p,c = 0,0   
    silence_sequence = [ele for ele in silence_sequence if not ele == None]   
    for silence in silence_sequence:        
        preset = [(arc.source,arc.weight) for arc in silence.in_arcs if obj[0]==arc.source.object_type]
        postset = [(arc.target,arc.weight) for arc in silence.out_arcs if obj[0]==arc.target.object_type]
        if all([len([o for o in marking[pl] if o==obj])>=weight for (pl,weight) in preset]):   
            p += sum([weight for (_,weight) in postset])
            c += sum([weight for (_,weight) in preset])
            for (pl,weight) in preset:
                marking[pl].remove(obj,multiplicity=weight)
            for (pl,weight) in postset:
                marking[pl].add(obj,multiplicity=weight)   
        else:
            raise ValueError(f'silence sequence {silence_sequence} cannot be executed')            
    return p,c