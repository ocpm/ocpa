from multiset import *

'''
rvalue: 1. whether cached or not, 2. the address of the cached value.
'''
def check_activity_caching(marking,obj,act,act_cache,exe_cache,marking_dict):
    reduced_map = reduce_marking(marking,obj)
    key = None
    for k,i in marking_dict.items():
        if i == reduced_map:
            key = k
            break
    if reduced_map in act_cache[act]:
        return True, exe_cache[(act,key)]
    elif key is None:
        key = index_marking(reduced_map,marking_dict)
        return False, key
    else:
        return False, key

def index_marking(reduced_map,marking_dict):
    if len(marking_dict.keys())==0:
        index = 0
    else:
        index = max([k for k in marking_dict.keys()])+1
    marking_dict[index] = reduced_map
    return index

'''
rvalue: the marking of a certain object
'''
def reduce_marking(marking,obj):
    reduced_map = Multiset()
    for pl in marking.keys():
        if obj in marking[pl]:
            reduced_map.add(pl.name,multiplicity=len([o for o in marking[pl] if o==obj]))
    return reduced_map