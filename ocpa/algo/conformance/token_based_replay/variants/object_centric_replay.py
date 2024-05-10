from multiset import *
import copy
from collections import Counter
import itertools
import ocpa.algo.conformance.token_based_replay.enhancement.address_token_flooding as address_token_flooding
import ocpa.algo.conformance.token_based_replay.enhancement.activity_caching as caching
import ocpa.algo.conformance.token_based_replay.backward_replay.algorithm as backward_replay_method
import ocpa.algo.conformance.token_based_replay.backward_replay.variants.backward_searching_tree as backward_searching_tree
import ocpa.algo.conformance.token_based_replay.backward_replay.variants.shortest_path as shortest_path

def apply(ocel,ocpn,parameters=None):
    '''
    Inputs:
    ocel: an object-centric event log.
    ocpn: an object-centric Petri net.
    ===================
    Parameters configuration (optional):
    'token_flooding': a dictionary of token flooding parameters, including:
                      'handle': whether to handle the token flooding.
                      'method': the method to detect superfluous tokens.
    'cache': a dictionary of caching parameters, including:
             'bst': whether to precompute BST for the resolution of backward replay.
             'activity': whether to cache the replay results for activity executions.
    ====================
    Return: a dictionary of evaluation results, including:

    'p': the number of produced tokens during the replay.
    'c': the number of consumed tokens during the replay.
    'm': the number of missing tokens during the replay.
    'r': the number of remaining tokens during the replay.
    'f': the number of frozen tokens during the replay.
    'is_equal': check whether the replay satisfies the flow conservation.
    'explicit_missing_tokens': the explicit missing tokens during the replay.
    'implicit_missing_tokens': the implicit missing tokens during the replay.
    'remaining_tokens': the remaining missing tokens during the replay.
    'frozen_tokens': the frozen tokens during the replay.
    'unenabled_transitions': the transitions unenabled for the execution during the replay.

    Further insights such as problematic places or objects could be extracted from the results above.
    '''
    if parameters == None:
        token_flooding = {'handle':True,'method':'S_component'}
        cache = {'bst':True,'activity':True}
    else:
        token_flooding = parameters['token_flooding']
        cache = parameters['cache']
    cached_execution,cached_act,marking,reduced_marking = {},{},{},{}
    initial_place,place_dict,transition_dict = {},{},{}
    information = {'explicit_missing_tokens':Multiset(),'unenabled_transitions':Multiset(),'frozen_tokens':Multiset(),'remaining_tokens':Multiset(),'implicit_missing_tokens':Multiset()}
    p,m,c,r,f = 0,0,0,0,0
    solved_backward_replay,unsolved_backward_replay = 0,0
    backward_possible_places = set()
    object_dict = ocel.obj.raw.objects
    final_places = [pl for pl in ocpn.places if pl.final]
    for ot in ocpn.object_types:
        initial_place[ot] = set()
    for pl in ocpn.places:
        place_dict[pl.name]=pl
        for a in pl.in_arcs:
            if a.source.silent:
                backward_possible_places.add(pl)
        marking[pl] = Multiset()
        if pl.initial:
            initial_place[pl.object_type].add(pl)
    for tr in ocpn.transitions:
        transition_dict[tr.label]=tr
        cached_act[tr] = []
    for fp in final_places:
        cached_act[fp] = []
    if token_flooding['handle']:
        S_components = address_token_flooding.calculate_S_component(ocpn)
    if any([a.weight>1 for a in ocpn.arcs]):   
        backward_replay = 'shortest_path'
    else:
        backward_replay = 'bst'      
    if backward_replay == 'bst':
        silence_constrain = backward_searching_tree.calculate_silence_constrain(ocpn)
        if cache['bst']:
            BST = backward_searching_tree.caching_bst(ocpn)
    elif backward_replay =='shortest_path':   
        dg = shortest_path.abstract_ocpn_to_DG(ocpn)
    event_list = list(ocel.obj.raw.events.items())
    sorted_event_list = sorted(event_list, key=lambda ele: ele[1].time)
    obj_list = list(itertools.chain(*ocel.process_execution_objects))

    '''
    Replay starts
    '''
    for obj in obj_list:
        for start_place in initial_place[obj[0]]:
            marking[start_place].add(obj)                
            p += 1
    for event_tuple in sorted_event_list:
        event = event_tuple[1]
        obj_list = [(object_dict[object_id].type,object_id) for object_id in event.omap]
        if event.act in transition_dict.keys():
            curr_tr = transition_dict[event.act]
        else:
            continue       
        preset = [arc.source for arc in curr_tr.in_arcs]
        postset = [arc.target for arc in curr_tr.out_arcs]
        '''
        Resolve implicit missing tokens
        '''
        for ot in [pl.object_type for pl in preset]:
            if not any([ot==ele[0] for ele in obj_list]):
                m += len([pl for pl in preset if ot==pl.object_type])
                c += len([pl for pl in preset if ot==pl.object_type])
                p += len([pl for pl in postset if ot==pl.object_type])
                f += len([pl for pl in postset if ot==pl.object_type])
                for pl in [pl for pl in preset if ot==pl.object_type]:
                    information['implicit_missing_tokens'].add((pl.name,'imp'))
                for pl in [pl for pl in postset if ot==pl.object_type]:
                    information['frozen_tokens'].add((pl.name,'imp'))
                information['unenabled_transitions'].add(curr_tr.label)
                
        '''
        Examine all involved objects
        '''     
        for obj in obj_list:
            preset = [(arc.source,arc.weight) for arc in curr_tr.in_arcs if arc.source.object_type == obj[0]]
            postset = [(arc.target,arc.weight) for arc in curr_tr.out_arcs if arc.target.object_type == obj[0]]      
            miss_places = [(pl,weight) for (pl,weight) in preset if not obj in marking[pl]]
            miss_places = [(pl,weight-len([o for o in marking[pl] if o==obj])) for (pl,weight) in preset if len([o for o in marking[pl] if o==obj])<weight]
            need_backward_replay = not all([not pl in backward_possible_places for (pl,w) in miss_places])
            object_marking = set()
            for k,i in marking.items():
                if obj in i:
                    object_marking.add(k)
            if not need_backward_replay:
                for (pl,weight) in preset:
                    if obj in marking[pl]:
                        marking[pl].remove(obj,multiplicity=weight)
                if token_flooding['handle']:
                    for (pl,_) in postset:
                        tf_parameters = {'current_place':pl,'S_component':S_components}                       
                        f0,frozen_tokens = address_token_flooding.solve_token_flooding(marking,pl,obj,token_flooding['method'],tf_parameters)                        
                        f += f0
                        information['frozen_tokens'] += frozen_tokens
                for (pl,weight) in postset:
                    marking[pl].add(obj,multiplicity=weight)
                c += sum([weight for (_,weight) in preset])
                p += sum([weight for (_,weight) in postset])
                m += sum([weight for (_,weight) in miss_places])
                for (pl,weight) in miss_places: 
                    information['explicit_missing_tokens'].add((pl.name,obj[1]),multiplicity=weight)
                if len(miss_places)>0:
                    information['unenabled_transitions'].add(curr_tr.label)              
            else:
                if cache['activity']:             
                    is_cached, mem = caching.check_activity_caching(marking,obj,curr_tr,cached_act,cached_execution,reduced_marking)
                else:
                    is_cached = False
                if is_cached:                                       
                    p_m = mem['p']
                    c_m = mem['c']
                    m_m = mem['m']
                    f_m = mem['f']
                    marking_before = mem['marking_before']
                    marking_after = mem['marking_after']
                    for pl in marking_before:
                        marking[pl].remove(obj,multiplicity=1)
                    for pl in marking_after:
                        marking[pl].add(obj)
                    p += p_m
                    c += c_m
                    m += m_m
                    f += f_m
                    information['explicit_missing_tokens'] += mem['explicit_missing_tokens']
                    if m_m>0:
                        information['unenabled_transitions'].add(mem['missing_transition']) 
                        unsolved_backward_replay += 1
                    else:
                        solved_backward_replay += 1
                    information['frozen_tokens'] += mem['frozen_tokens']
                else:
                    cached_act[curr_tr].append(caching.reduce_marking(marking,obj))
                    marking_before = Multiset()
                    for pl in marking:
                        if obj in marking[pl]:
                            marking_before.add(pl,multiplicity=len([o for o in marking[pl] if o==obj]))
                    if backward_replay == 'bst':
                        if cache['bst']:
                            cached_BST = BST[(curr_tr,obj[0])]
                            cached_BST.constrains = backward_searching_tree.calculate_bst_constrain(cached_BST,silence_constrain)
                            p0,c0,m0,info_backward_replay = backward_replay_method.cashed_bst_backward_replay(marking,obj,cached_BST)
                        else:                
                            p0,c0,m0,info_backward_replay = backward_replay_method.bst_backward_replay(curr_tr,marking,obj,silence_constrain)
                    elif backward_replay == 'shortest_path':
                        dg_copy = copy.deepcopy(dg)                                
                        parameters = {'preset':preset,'transition_dict':transition_dict,'place_dict':place_dict}
                        p0,c0,m0,info_backward_replay = backward_replay_method.shortest_path_backward_replay(ocpn,dg_copy,marking,obj,parameters)
                    else:
                        raise ValueError(f'Silence resolution {backward_replay} is not defined')
                    
                    p += p0
                    c += c0
                    m += m0
                    for (pl,weight) in info_backward_replay['missing_places']:
                        information['explicit_missing_tokens'].add((pl.name,obj[1]),multiplicity=weight)
                    if m0 > 0:
                        information['unenabled_transitions'].add(curr_tr.label)
                        unsolved_backward_replay += 1
                    else:
                        solved_backward_replay += 1

                    for (pl,weight) in preset:
                        marking[pl].remove(obj,multiplicity=weight)
                    if token_flooding['handle']:
                        for (pl,_) in postset:
                            tf_parameters = {'current_place':pl,'S_component':S_components}                       
                            f0,frozen_tokens = address_token_flooding.solve_token_flooding(marking,pl,obj,token_flooding['method'],tf_parameters)                        
                            f += f0
                            information['frozen_tokens'] += frozen_tokens
                    for (pl,weight) in postset:
                        marking[pl].add(obj,multiplicity=weight)
                    c += sum([weight for (_,weight) in preset])
                    p += sum([weight for (_,weight) in postset])                    
                    
                    marking_after = Multiset()
                    for pl in marking:
                        if obj in marking[pl]:
                            marking_after.add(pl,multiplicity=len([o for o in marking[pl] if o==obj]))
                    if cache['activity']:  
                        caching_execution = {}
                        caching_execution['p'] = p0+sum([weight for (_,weight) in postset])
                        caching_execution['c'] = c0+sum([weight for (_,weight) in preset])
                        caching_execution['m'] = m0
                        if token_flooding['handle']:
                            caching_execution['f'] = f0
                            caching_execution['frozen_tokens'] = frozen_tokens
                        else:
                            caching_execution['f'] = 0
                            caching_execution['frozen_tokens'] = Multiset()
                        caching_execution['marking_before'] = marking_before - (marking_before & marking_after)
                        caching_execution['marking_after'] = marking_after - (marking_before & marking_after)
                        caching_execution['explicit_missing_tokens'] = Multiset()
                        for (pl,w) in info_backward_replay['missing_places']:
                            caching_execution['explicit_missing_tokens'].add((pl.name,obj[1]),multiplicity=w)
                        caching_execution['missing_transition'] = curr_tr.label if m0 > 0 else None
                        key = mem
                        cached_execution[(curr_tr,key)] = caching_execution

    for pl in final_places:
        c += len(marking[pl])
        marking[pl] = Multiset()

    '''
    Examine remaining tokens
    '''
    for pl1 in final_places:
        if len([a for a in pl1.in_arcs if a.source.silent]) == 0:
            for pl2 in ocpn.places:
                bounded_obj = copy.deepcopy(marking[pl2])
                for o in bounded_obj:
                    if o[0] == pl1.object_type:
                        marking[pl2].remove(o,multiplicity=1)
                        c += 1
                        r += 1
                        m += 1
                        information['explicit_missing_tokens'].add((pl1.name,o[1]))
                        information['remaining_tokens'].add((pl2.name,o[1]))

    remaining_places = [pl for pl in ocpn.places-set(final_places) if len(marking[pl])>0] 
    remaining_objects = Multiset().union(*[marking[pl] for pl in remaining_places])
    remaining_iteration_count = 0
    while remaining_objects:
        for obj in remaining_objects:            
            obj_final_places = [pl for pl in ocpn.places if pl.final and pl.object_type==obj[0]]            
            if len(obj_final_places) > 1:
                raise ValueError('the end place is not unique for an object type')
            final_place = obj_final_places[0]
            if cache['activity']:
                is_cached, mem = caching.check_activity_caching(marking,obj,final_place,cached_act,cached_execution,reduced_marking)
            else:
                is_cached = False
            if is_cached:
                p0 = mem['p']
                c0 = mem['c']
                m0 = mem['m']
                r0 = mem['r']
                marking_before = mem['marking_before']
                marking_after = mem['marking_after']
                for pl in marking_before:
                    marking[pl].remove(obj,multiplicity=1)
                for pl in marking_after:
                    marking[pl].add(obj)
                p += p0
                c += c0
                m += m0
                r += r0
                information['explicit_missing_tokens'] += mem['explicit_missing_tokens']
                if m0>0:
                    information['remaining_tokens'].add(mem['remaining_token']) 
                    unsolved_backward_replay += 1
                else:
                    solved_backward_replay += 1                
            else:
                cached_act[final_place].append(caching.reduce_marking(marking,obj))
                marking_before = Multiset()
                for pl in marking:
                    if obj in marking[pl]:
                        marking_before.add(pl,multiplicity=len([o for o in marking[pl] if o==obj]))
                object_marking = {}
                for k,i in marking.items():
                    if obj in i:
                        object_marking[k] = copy.deepcopy(i)
                if backward_replay == 'bst':
                    if cache['bst']:                            
                        cached_BST = BST[(*obj_final_places,obj[0])]
                        cached_BST.constrains=backward_searching_tree.calculate_bst_constrain(cached_BST,silence_constrain)                       
                        p0,c0,m0,info_backward_replay = backward_replay_method.cashed_bst_backward_replay(marking,obj,cached_BST)                                             
                    else:           
                        if len(obj_final_places)==1:
                            p0,c0,m0,info_backward_replay = backward_replay_method.bst_backward_replay(*obj_final_places,marking,obj,silence_constrain)
                        else:
                            return ValueError('The final place is not unique for a certain object type!')
                elif backward_replay == 'shortest_path':
                    dg_copy = copy.deepcopy(dg)
                    parameters = {'preset':[(p,1) for p in obj_final_places],'transition_dict':transition_dict,'place_dict':place_dict}
                    p0,c0,m0,info_backward_replay = backward_replay_method.shortest_path_backward_replay(ocpn,dg_copy,marking,obj,parameters)            
                r0 = 0
                remaining_token = None
                for (pl,w) in info_backward_replay['missing_places']:
                    information['explicit_missing_tokens'].add((pl.name,obj[1]),multiplicity=w) 
                if m0>0:
                    for pl in ocpn.places-set(final_places):
                        if obj in marking[pl]:
                            res_token = len([o for o in marking[pl] if o==obj])
                            marking[pl].remove(obj,multiplicity=res_token) 
                            r0 += res_token
                            remaining_token = (pl.name,obj[1])
                            information['remaining_tokens'].add((pl.name,obj[1]),multiplicity=res_token)
                            unsolved_backward_replay += 1
                            break
                    c0 = r0
                    m0 = r0 
                else:
                    solved_backward_replay += 1
                    c0 += 1                     
                marking[final_place].remove(obj,multiplicity=1) 
                #c0 += 1     
                p += p0
                c += c0
                m += m0
                r += r0
                                                         
                marking_after = Multiset()
                for pl in marking:
                    if obj in marking[pl]:
                        marking_after.add(pl,multiplicity=len([o for o in marking[pl] if o==obj]))           
                if cache['activity']:  
                    caching_execution = {}
                    caching_execution['p'] = p0
                    caching_execution['c'] = c0
                    caching_execution['m'] = m0
                    caching_execution['r'] = r0
                    caching_execution['marking_before'] = marking_before - (marking_before & marking_after)
                    caching_execution['marking_after'] = marking_after - (marking_before & marking_after)
                    caching_execution['explicit_missing_tokens'] = Multiset()
                    for (pl,w) in info_backward_replay['missing_places']:
                        caching_execution['explicit_missing_tokens'].add((pl.name,obj[1]),multiplicity=w)
                    if r0>0:
                        caching_execution['remaining_token'] = remaining_token      
                    key = mem
                    cached_execution[(final_place,key)] = caching_execution
            remaining_iteration_count += 1
        remaining_objects = set().union(*[marking[pl] for pl in ocpn.places])
    if c == 0 or p == 0:
        raise ValueError('No consumed or produced tokens')

    result = {'fitness':1/2*(1-m/c)+1/2*(1-(r+f)/p),'p':p,'c':c,'m':m,'r':r,'f':f,'is_equal':p+m==r+c+f,\
              'solved_backward_replay':solved_backward_replay,'unsolved_backward_replay':unsolved_backward_replay}
    result['explicit_missing_tokens'] = Counter(list(information['explicit_missing_tokens']))
    result['unenabled_transitions'] = Counter(list(information['unenabled_transitions']))
    result['remaining_tokens'] = Counter(list(information['remaining_tokens']))
    result['implicit_missing_tokens'] = Counter(list(information['implicit_missing_tokens']))
    result['frozen_tokens'] = Counter(list(information['frozen_tokens']))

    return result
