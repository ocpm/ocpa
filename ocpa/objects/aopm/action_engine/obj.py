from typing import List, Dict, Set, Any, Optional, Union, Tuple
import networkx as nx
import itertools

class ConstraintInstance:
    def __init__(self, name, start, end):
        if start <= end:
            self.name = name
            self.start = start
            self.end = end
        else:
            raise ValueError("Start time must be less than or equal to end time")

    def __str__(self):
        return f"{self.name}: [{self.start}, {self.end}]"
    
    def __repr__(self):
        return f"{self.name}({self.start}, {self.end})"

    def merge(self, other):
        return ConstraintInstance("-".join([self.name, other.name]), min(self.start, other.start), max(self.end, other.end))

    def overlaps(self, other):
        return not (self.end < other.start or other.end < self.start)

class ConstraintPattern:
    def __init__(self):
        self.tree = nx.DiGraph()
        self.root = None
        self.labels = {}

    def _str_traversal(self, node):
        if node is not None:
            children = list(self.tree.successors(node))
            result = f"{self.labels[node]}"
            if len(children) > 0:
                result += self._str_traversal(children[0])
            if len(children) > 1:
                result += self._str_traversal(children[1])
            return result
        else:
            return ""

    def __str__(self):
        return self._str_traversal(self.root)

    def add_root(self, node_id, label):
        if self.root is None:
            self.root = node_id
            self.tree.add_node(node_id)
            self.labels[node_id] = label
        else:
            raise ValueError("Root already exists")

    def add_left_child(self, parent, node_id, label):
        if self.tree.has_node(parent):
            children = list(self.tree.successors(parent))
            if len(children) < 2:
                self.tree.add_node(node_id)
                self.tree.add_edge(parent, node_id)
                self.labels[node_id] = label
            else:
                raise ValueError("Parent already has two children")
        else:
            self.tree.add_node(node_id)
            raise ValueError("Parent not found in the tree")

    def add_right_child(self, parent, node_id, label):
        if self.tree.has_node(parent):
            children = list(self.tree.successors(parent))
            if len(children) < 1:
                self.tree.add_node(node_id)
                self.tree.add_edge(parent, node_id)
                self.labels[node_id] = label
            elif len(children) < 2:
                self.tree.add_node(node_id)
                self.tree.add_edge(parent, node_id)
                self.labels[node_id] = label
            else:
                raise ValueError("Parent already has two children")
        else:
            raise ValueError("Parent not found in the tree")

    def in_order_traversal(self, node, collector):
        if node is not None:
            children = list(self.tree.successors(node))
            if len(children) > 0:
                self.in_order_traversal(children[0], collector)
            collector.append(node)
            print(self.labels[node])
            if len(children) > 1:
                self.in_order_traversal(children[1], collector)
        return collector

    def pre_order_traversal(self, node):
        if node is not None:
            print(self.labels[node])
            children = list(self.tree.successors(node))
            if len(children) > 0:
                self.pre_order_traversal(children[0])
            if len(children) > 1:
                self.pre_order_traversal(children[1])

    def post_order_traversal(self, node, collector):
        if node is not None:
            children = list(self.tree.successors(node))
            if len(children) > 0:
                self.post_order_traversal(children[0], collector)
            if len(children) > 1:
                self.post_order_traversal(children[1], collector)
            collector.append(node)
            print(self.labels[node])
        return collector

    def get_inner_nodes(self):
        inner_nodes = [node for node in self.tree.nodes() if self.tree.out_degree(node) > 0]
        return inner_nodes

    def get_left_leaves(self, node):
        left_leaves = []
        children = list(self.tree.successors(node))
        if len(children) > 0:
            left_child = children[0]
            if self.tree.out_degree(left_child) == 0:
                left_leaves.append(left_child)
            else:
                left_leaves.extend(self.get_left_leaves(left_child))
                left_leaves.extend(self.get_right_leaves(left_child))
        return left_leaves

    def get_right_leaves(self, node):
        right_leaves = []
        children = list(self.tree.successors(node))
        if len(children) > 1:
            right_child = children[1]
            if self.tree.out_degree(right_child) == 0:
                right_leaves.append(right_child)
            else:
                right_leaves.extend(self.get_left_leaves(right_leaves))
                right_leaves.extend(self.get_right_leaves(right_child))
        return right_leaves

    def get_leaves(self, node=None):
        if node is None:
            node = self.root

        leaves = []
        children = list(self.tree.successors(node))
        if len(children) == 0:
            leaves.append(node)
        else:
            for child in children:
                leaves.extend(self.get_leaves(child))
        return leaves

        
        

    # possible_mappings: List[Dict[str,ConstraintInstance]] = []

    # def get_mappings_with_nodes(mappings:List[Dict[str,ConstraintInstance]], nodes:List[str]):
    #     mappings_with_nodes = []
    #     for mapping in mappings:
    #         if all([node in mapping for node in nodes]):
    #             mappings_with_nodes.append(mapping)
    #     return mappings_with_nodes

    # for i in range(len(eval_inner_nodes)):
    #     eval_node = eval_inner_nodes[i]
    #     if i == 0:
    #         left_leaves = cp.get_left_leaves(eval_node)
    #         if len(left_leaves) != 1:
    #             raise ValueError("Left leaves should be one")
    #         else:
    #             left_leaf = left_leaves[0]
    #             for ci in cis:
    #                 if ci.label == cp.labels[left_leaf]:
    #                     possible_mappings.append({left_leaf:ci})
    #         right_leaves = cp.get_right_leaves(eval_node)
    #         if len(right_leaves) != 1:
    #             raise ValueError("Right leaves should be one")
    #         else:
    #             right_leaf = right_leaves[0]
    #             for ci in cis:
    #                 if ci.label == cp.labels[right_leaf]:
    #                     for mapping in possible_mappings:
    #                         if allens_relation(mapping[left_leaf].interval, ci.interval, cp.labels[eval_node]):
    #                             mapping[right_leaf] = ci
    #     else:
    #         left_leaves = cp.get_left_leaves(eval_node)
    #         left_valid_mappings = get_mappings_with_nodes(possible_mappings, left_leaves)
            
            
    #         right_leaves = cp.get_right_leaves(eval_node)
    #         right_leaf = right_leaves[0]
    #         for ci in cis:
    #             if ci.label == cp.labels[right_leaf]:
    #                 for mapping in possible_mappings:
    #                     if allens_relation(mapping[left_leaf].interval, ci.interval, cp.labels[eval_node]):
    #                         mapping[right_leaf] = ci

    # for eval_node in eval_inner_nodes:
    #     left_leaves = cp.get_left_leaves(eval_node)
    #     right_leaves = cp.get_right_leaves(eval_node)

    #     for leaf in left_leaves:
    #         if leaf in mappings:
    #         print(cp.labels[leaf])



if __name__ == "__main__":
    bt = ConstraintPattern()
    bt.add_root(1, "overlaps")
    bt.add_left_child(1, 2, "before")
    bt.add_right_child(1, 3, "G3")
    bt.add_left_child(2, 4, "G1")
    bt.add_right_child(2, 5, "G2")

    print(bt.get_inner_nodes())

    print(bt.get_left_leaves(1))
    print(bt.get_right_leaves(1))

    ci1 = ConstraintInstance(name="G1", start=0, end=10)
    ci2 = ConstraintInstance(name="G2", start=5, end=15)
    ci3 = ConstraintInstance(name="G3", start=10, end=20)
    cis1 = [ci1, ci2, ci3]

    ci1 = ConstraintInstance(name="G1", start=0, end=3)
    ci2 = ConstraintInstance(name="G2", start=5, end=15)
    ci3 = ConstraintInstance(name="G3", start=10, end=20)
    cis2 = [ci1, ci2, ci3]

    apply(cis1,bt)
    apply(cis2,bt)
