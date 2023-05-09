from typing import List, Dict, Set, Any, Optional, Union, Tuple
from ocpa.objects.aopm.action_engine.obj import ConstraintInstance, ConstraintPattern, ActionInstance, ActionCandidate, ActionGraph
import itertools
import networkx as nx
import time
from datetime import datetime, timedelta
from dateutil.parser import parse

def apply(cis:List[ConstraintInstance], action_graph:List[ActionGraph], precedence_relations: List[Tuple[str,str]], time_scale: str = "hour") -> List[ActionInstance]:
    default_action_date = latest_end_date(cis)
    action_candidates = []
    for ag in action_graph:
        cp,action,dur = ag.pattern, ag.action, ag.duration
        mappings = generate_all_possible_mappings(cp,cis)
        eval_inner_nodes = [x for x in cp.post_order_traversal(cp.root, []) if x in cp.get_inner_nodes()]
        is_valid = True
        for mapping in mappings:
            for eval_node in eval_inner_nodes:
                left_leaves = cp.get_left_leaves(eval_node)
                left_cis = [mapping[leaf] for leaf in left_leaves]
                left_merged_ci = merge(left_cis)
                right_leaves = cp.get_right_leaves(eval_node)
                right_cis = [mapping[leaf] for leaf in right_leaves]
                right_merged_ci = merge(right_cis)
                if allens_relation(left_merged_ci, right_merged_ci, cp.labels[eval_node]) == False:
                    is_valid = False
                    # once any relation does not fit, we can stop evaluating this mapping
                    break
            if is_valid:
                print("Valid mapping: ", mapping)
                # once we find a valid mapping, we can stop evaluating other mappings
                break
        if is_valid:
            action_candidates.append(ActionCandidate(action,dur))
    
    def filter_longest_duration_candidates(candidates):
        longest_duration_per_action = {}
        for candidate in candidates:
            if candidate.action not in longest_duration_per_action:
                longest_duration_per_action[candidate.action] = candidate
            elif candidate.duration > longest_duration_per_action[candidate.action].duration:
                longest_duration_per_action[candidate.action] = candidate
        return list(longest_duration_per_action.values())
    
    filtered_candidates = filter_longest_duration_candidates(action_candidates)

    action_conflict = create_action_conflict(precedence_relations)
    
    action_instances, time_performance, makespan, total_waiting_time, total_flow_time = plan_actions(filtered_candidates, action_conflict)
    action_instances_with_default_date = enhance_to_absolute_time(action_instances, default_action_date, time_scale)
    return action_instances_with_default_date

def latest_end_date(constraint_instances):
    max_end_date = None
    
    for ci in constraint_instances:
        if max_end_date is None or ci.end > max_end_date:
            max_end_date = ci.end
            
    return max_end_date
    

def generate_all_possible_mappings(cp: ConstraintPattern, constraint_instances: List[ConstraintInstance]):
        leaves = cp.get_leaves()
        mappings = list(itertools.product(constraint_instances, repeat=len(leaves)))

        all_mappings = []
        for mapping in mappings:
            is_valid = True
            for leaf, constraint in zip(leaves, mapping):
                if cp.labels[leaf] != constraint.name:
                    is_valid = False
                    break

            if is_valid:
                all_mappings.append(dict(zip(leaves, mapping)))
        
        return all_mappings


def complete_allens_relation(interval, other, relation:str):
        if relation == "before":
            return interval.end < other.start
        elif relation == "equal":
            return interval.start == other.start and interval.end == other.end
        elif relation == "meets":
            return interval.end == other.start
        elif relation == "overlaps":
            return interval.start < other.start and interval.end < other.end
        elif relation == "during":
            return other.start < interval.start and other.end > interval.end
        elif relation == "starts":
            return interval.start == other.start
        elif relation == "finishes":
            return interval.end == other.end
        else: 
            raise ValueError("Relation not found")

def allens_relation(interval, other, relation:str):
        if relation == "before":
            return interval.end < other.start
        elif relation == "equal":
            return interval.start == other.start and interval.end == other.end
        elif relation == "overlaps":
            return interval.start <= other.start and interval.end < other.end
        elif relation == "during":
            return other.start <= interval.start and other.end >= interval.end
        else: 
            raise ValueError("Relation not found")

def merge(cis:List[ConstraintInstance]):
        return ConstraintInstance("-".join([x.name for x in cis]), min([x.start for x in cis]), max([x.end for x in cis]))


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap

def create_action_conflict(precedence_relations):
    if type(precedence_relations) == list:
        G = nx.DiGraph()
        for a, b in precedence_relations:
            G.add_edge(a, b)
    elif type(precedence_relations) == nx.DiGraph:
        G = precedence_relations
    return G

@timing
def instantiate_action_conflict(action_candidates, action_conflict):
    G = nx.DiGraph()
    G.add_nodes_from(action_candidates)
    for a, b in itertools.permutations(action_candidates, 2):
        if (a.action, b.action) in action_conflict.edges():
            G.add_edge(a, b)
    return G


def complete(scheduled,t):
    return [a for a, finish in scheduled if finish <= t]

def plan_actions(action_candidates, action_conflict):
    action_instances = []
    scheduled = []
    t = 0
    instantiated_action_conflict = instantiate_action_conflict(action_candidates,action_conflict)
    time1 = time.time()
    while len(action_candidates) != 0:
        for can in action_candidates[:]:
            required = set([a for a, b in instantiated_action_conflict.in_edges(can)])
            completed = set(complete(scheduled,t+1))
            proceed = required.issubset(completed)
            if proceed:
                action_candidates.remove(can)
                scheduled.append((can, can.duration+t+1))
                action_instances.append(ActionInstance(can.action, t+1, t+1+can.duration))
        t += 1
    time2 =  time.time()
    time_performance = round((time2 - time1)*1000.0,3)
    if len(action_instances) >0:
        makespan = max([ai.end for ai in action_instances])
    else:
        makespan = 0
    total_waiting_time = compute_total_waiting_time(action_instances)
    total_flow_time = compute_total_flow_time(action_instances)
    print('planning took {:.3f} ms'.format((time_performance)))
    print(f'makespan: {makespan}')
    print(f'total waiting time: {total_waiting_time}')
    print(f'total flow time: {total_flow_time}')
    return action_instances, time_performance, makespan, total_waiting_time, total_flow_time

def compute_total_waiting_time(action_instances: List[ActionInstance]):
    return sum([ai.start-1 for ai in action_instances])

def compute_total_flow_time(action_instances: List[ActionInstance]):
    return sum([ai.end-1 for ai in action_instances])

def enhance_to_absolute_time(action_instances, date, time_scale):
    time_scale = time_scale.lower()

    for action_instance in action_instances:
        if time_scale == "hour":
            action_instance.start = date + timedelta(hours=action_instance.start)
            action_instance.end = date + timedelta(hours=action_instance.end)
        elif time_scale == "day":
            action_instance.start = date + timedelta(days=action_instance.start)
            action_instance.end = date + timedelta(days=action_instance.end)
        elif time_scale == "month":
            action_instance.start = date + timedelta(days=30 * action_instance.start)
            action_instance.end = date + timedelta(days=30 * action_instance.end)
        else:
            raise ValueError("Unsupported time scale")

    return action_instances
