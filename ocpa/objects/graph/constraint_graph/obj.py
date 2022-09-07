from dataclasses import dataclass, field
from typing import List, Dict, Set, Any, Optional, Union, Tuple


@dataclass(unsafe_hash=True)
class ActivityNode:
    name: str


@dataclass(unsafe_hash=True)
class ObjectTypeNode:
    name: str


@dataclass(unsafe_hash=True)
class FormulaNode:
    diag: str
    comparator: str
    threshold: int
    agg: str = None
    object_type: str = None

    # def __repr__(self) -> str:
    #     if self.object_type is not None and self.agg is not None:
    #         return f"{self.agg} {self.diag} of {self.object_type} {self.comparator} {self.threshold}"
    #     elif self.object_type is None and self.agg is not None:
    #         return f"{self.agg} {self.diag} {self.comparator} {self.threshold}"
    #     elif self.object_type is not None and self.agg is None:
    #         return f"{self.diag} of {self.object_type} {self.comparator} {self.threshold}"
    #     elif self.object_type is None and self.agg is None:
    #         return f"{self.diag} {self.comparator} {self.threshold}"
    #     else:
    #         f"{self.agg} {self.diag} {self.object_type} {self.comparator} {self.threshold}"


@dataclass(unsafe_hash=True)
class ControlFlowEdge:
    source: ActivityNode
    target: ActivityNode
    label: str
    object_type: str
    threshold: float

    def message(self, strength) -> str:
        if self.label == 'causal':
            return f'{self.source.name} causes {self.target.name} (strength: {round(strength,2)}).'
        elif self.label == 'concur':
            return f'{self.source.name} and {self.target.name} are concurrently executed (strength: {round(strength,2)}).'
        elif self.label == 'choice':
            return f'Either {self.source.name} or {self.target.name} is executed (strength: {round(strength,2)}).'
        elif self.label == 'skip':
            if self.source.name == self.target.name:
                return f'{self.source.name} is skipped (strength: {round(strength,2)}).'
            else:
                raise ValueError(
                    f'{self.source.name} and {self.target.name} should be identical.')
        else:
            raise ValueError(f'{self.label} is undefined.')


@dataclass(unsafe_hash=True)
class ObjectRelationEdge:
    source: ObjectTypeNode
    target: ActivityNode
    label: str
    threshold: float

    def message(self, strength) -> str:
        if self.label == 'absent':
            return f'{self.target.name} does not involve {self.source.name} for its execution (strength: {round(strength,2)}).'
        elif self.label == 'present':
            return f'{self.target.name} unnecessarily involves {self.source.name} for its execution (strength: {round(strength,2)}).'
        elif self.label == 'singular':
            return f'{self.target.name} invovles only one {self.source.name} per execution (strength: {round(strength,2)}).'
        elif self.label == 'multiple':
            return f'{self.target.name} involves multiple orders for its execution (strength: {round(strength,2)}).'
        else:
            raise ValueError(f'{self.label} is undefined.')


@dataclass(unsafe_hash=True)
class PerformanceEdge:
    source: FormulaNode
    target: ActivityNode

    @property
    def message(self) -> str:
        if self.source.object_type is not None:
            if self.source.agg is not None:
                return f'At {self.target.name}, {self.source.agg} of {self.source.diag} by {self.source.object_type} {self.source.comparator} {self.source.threshold}'
            else:
                return f'At {self.target.name}, {self.source.diag} by {self.source.object_type} {self.source.comparator} {self.source.threshold}'
        else:
            if self.source.agg is not None:
                return f'At {self.target.name}, {self.source.agg} of {self.source.diag} {self.source.comparator} {self.source.threshold}'
            else:
                return f'At {self.target.name}, {self.source.diag} {self.source.comparator} {self.source.threshold}'


@dataclass(unsafe_hash=True)
class ConstraintGraph:
    name: str
    nodes: Union[Set[ActivityNode],
                 Set[ObjectTypeNode], Set[FormulaNode]] = field(default_factory=set)
    cf_edges: Set[ControlFlowEdge] = field(default_factory=set)
    obj_edges: Set[ObjectRelationEdge] = field(default_factory=set)
    perf_edges: Set[PerformanceEdge] = field(default_factory=set)
    # cf_label: Dict[ControlFlowEdge, Set[str]]
    # obj_label: Dict[ObjectRelationEdge, Set[str]]

    def add_node(self, node):
        self.nodes.add(node)

    def add_nodes(self, nodes):
        if isinstance(nodes, list):
            nodes = set(nodes)
        self.nodes = self.nodes | nodes

    def add_cf_edge(self, cf_edge):
        self.cf_edges.add(cf_edge)

    def add_cf_edges(self, cf_edges):
        self.cf_edges = self.cf_edges | cf_edges

    def add_obj_edge(self, obj_edge):
        self.obj_edges.add(obj_edge)

    def add_obj_edges(self, obj_edges):
        self.obj_edges = self.obj_edges | obj_edges

    def add_perf_edge(self, perf_edge):
        self.perf_edges.add(perf_edge)

    def add_perf_edges(self, perf_edges):
        self.perf_edges = self.perf_edges | perf_edges
