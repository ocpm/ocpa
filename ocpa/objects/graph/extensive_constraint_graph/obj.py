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


@dataclass(unsafe_hash=True)
class OAEdge:
    source: ObjectTypeNode
    target: ActivityNode
    label: str
    operator: str
    threshold: float

    # def message(self, strength) -> str:
    #     if self.label == 'causal':
    #         return f'{self.source.name} causes {self.target.name} (strength: {round(strength,2)}).'
    #     elif self.label == 'concur':
    #         return f'{self.source.name} and {self.target.name} are concurrently executed (strength: {round(strength,2)}).'
    #     elif self.label == 'choice':
    #         return f'Either {self.source.name} or {self.target.name} is executed (strength: {round(strength,2)}).'
    #     elif self.label == 'skip':
    #         if self.source.name == self.target.name:
    #             return f'{self.source.name} is skipped (strength: {round(strength,2)}).'
    #         else:
    #             raise ValueError(
    #                 f'{self.source.name} and {self.target.name} should be identical.')
    #     else:
    #         raise ValueError(f'{self.label} is undefined.')


@dataclass(unsafe_hash=True)
class AAEdge:
    source: ActivityNode
    target: ActivityNode
    label: str
    operator: str
    threshold: float

    # def message(self, strength) -> str:
    #     if self.label == 'absent':
    #         return f'{self.target.name} does not involve {self.source.name} for its execution (strength: {round(strength,2)}).'
    #     elif self.label == 'present':
    #         return f'{self.target.name} unnecessarily involves {self.source.name} for its execution (strength: {round(strength,2)}).'
    #     elif self.label == 'singular':
    #         return f'{self.target.name} invovles only one {self.source.name} per execution (strength: {round(strength,2)}).'
    #     elif self.label == 'multiple':
    #         return f'{self.target.name} involves multiple orders for its execution (strength: {round(strength,2)}).'
    #     else:
    #         raise ValueError(f'{self.label} is undefined.')


@dataclass(unsafe_hash=True)
class AOAEdge:
    source: ActivityNode
    inner: ObjectTypeNode
    target: ActivityNode
    label: str
    operator: str
    threshold: float

    # @property
    # def message(self) -> str:
    #     if self.source.object_type is not None:
    #         if self.source.agg is not None:
    #             return f'At {self.target.name}, {self.source.agg} of {self.source.diag} by {self.source.object_type} {self.source.comparator} {self.source.threshold}'
    #         else:
    #             return f'At {self.target.name}, {self.source.diag} by {self.source.object_type} {self.source.comparator} {self.source.threshold}'
    #     else:
    #         if self.source.agg is not None:
    #             return f'At {self.target.name}, {self.source.agg} of {self.source.diag} {self.source.comparator} {self.source.threshold}'
    #         else:
    #             return f'At {self.target.name}, {self.source.diag} {self.source.comparator} {self.source.threshold}'


@dataclass(unsafe_hash=True)
class ExtensiveConstraintGraph:
    name: str
    nodes: Union[Set[ActivityNode], Set[ObjectTypeNode]
                 ] = field(default_factory=set)
    oa_edges: Set[OAEdge] = field(default_factory=set)
    aa_edges: Set[AAEdge] = field(default_factory=set)
    aoa_edges: Set[AOAEdge] = field(default_factory=set)

    def add_node(self, node):
        self.nodes.add(node)

    def add_nodes(self, nodes):
        if isinstance(nodes, list):
            nodes = set(nodes)
        self.nodes = self.nodes | nodes

    def add_oa_edge(self, oa_edge):
        self.oa_edges.add(oa_edge)

    def add_oa_edges(self, oa_edges):
        self.oa_edges = self.oa_edges | oa_edges

    def add_aa_edge(self, aa_edge):
        self.aa_edges.add(aa_edge)

    def add_aa_edges(self, aa_edges):
        self.aa_edges = self.aa_edges | aa_edges

    def add_aoa_edge(self, aoa_edge):
        self.aoa_edges.add(aoa_edge)

    def add_aoa_edges(self, aoa_edges):
        self.aoa_edges = self.aoa_edges | aoa_edges
