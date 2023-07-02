from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Union, Tuple
import networkx as nx
import datetime

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
    def __init__(self, name):
        self.name = name
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

    # def add_left_child(self, parent, node_id, label):
    #     if self.tree.has_node(parent):
    #         children = list(self.tree.successors(parent))
    #         if len(children) < 2:
    #             self.tree.add_node(node_id)
    #             self.tree.add_edge(parent, node_id)
    #             self.labels[node_id] = label
    #         else:
    #             raise ValueError("Parent already has two children")
    #     else:
    #         self.tree.add_node(node_id)
    #         raise ValueError("Parent not found in the tree")

    # def add_right_child(self, parent, node_id, label):
    #     if self.tree.has_node(parent):
    #         children = list(self.tree.successors(parent))
    #         if len(children) < 1:
    #             self.tree.add_node(node_id)
    #             self.tree.add_edge(parent, node_id)
    #             self.labels[node_id] = label
    #         elif len(children) < 2:
    #             self.tree.add_node(node_id)
    #             self.tree.add_edge(parent, node_id)
    #             self.labels[node_id] = label
    #         else:
    #             raise ValueError("Parent already has two children")
    #     else:
    #         raise ValueError(f"Parent {parent} not found in the tree: {self.tree.nodes()}")

    def add_left_child(self, parent, node_id, label):
        if not self.tree.has_node(parent):
            self.tree.add_node(parent)
            self.labels[parent] = None

        children = list(self.tree.successors(parent))
        if len(children) < 2:
            self.tree.add_node(node_id)
            self.tree.add_edge(parent, node_id)
            self.labels[node_id] = label
        else:
            raise ValueError("Parent already has two children")

    def add_right_child(self, parent, node_id, label):
        if not self.tree.has_node(parent):
            self.tree.add_node(parent)
            self.labels[parent] = None

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

        
@dataclass()
class ActionGraph:
    pattern: ConstraintPattern
    action: str
    duration: int
    time_scale: str = "hours"


@dataclass()
class ActionInstance:
    action: str
    start: datetime.datetime
    end: datetime.datetime


@dataclass(unsafe_hash=True)
class ActionCandidate:
    action: str
    duration: int

    def __repr__(self) -> str:
        return self.action



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
