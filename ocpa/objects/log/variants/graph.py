from dataclasses import dataclass
import networkx as nx

@dataclass
class EventGraph:
    eog: nx.DiGraph

