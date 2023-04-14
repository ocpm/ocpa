from dataclasses import dataclass
import networkx as nx


@dataclass
class ObjectGraph:
    eog: nx.Graph