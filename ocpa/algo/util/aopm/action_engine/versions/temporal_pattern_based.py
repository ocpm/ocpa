from typing import List, Dict, Set, Any, Optional, Union, Tuple
from ocpa.objects.aopm.action_engine.obj import ConstraintInstance, ConstraintPattern
import itertools

def apply(cis:List[ConstraintInstance], cp:ConstraintPattern) -> bool:
    mappings = generate_all_possible_mappings(cp,cis)
    for mapping in mappings:
        print(mapping)
    
    eval_inner_nodes = [x for x in cp.post_order_traversal(cp.root, []) if x in cp.get_inner_nodes()]
    for mapping in mappings:
        is_valid = True
        for eval_node in eval_inner_nodes:
            left_leaves = cp.get_left_leaves(eval_node)
            left_cis = [mapping[leaf] for leaf in left_leaves]
            left_merged_ci = merge(left_cis)
            right_leaves = cp.get_right_leaves(eval_node)
            right_cis = [mapping[leaf] for leaf in right_leaves]
            right_merged_ci = merge(right_cis)
            if allens_relation(left_merged_ci, right_merged_ci, cp.labels[eval_node]) == False:
                is_valid = False
                break
        if is_valid:
            print("Valid mapping: ", mapping)
            return True
    return False
    

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
