import networkx as nx
from ocpa.objects.event_graph.obj import EventGraph
import matplotlib.pyplot as plt


def apply(ocel):
    events = [ocel.raw.events[ei] for ei in ocel.raw.events]
    objects = ocel.raw.objects
    graph = nx.DiGraph()
    graph.add_nodes_from(events)
    edges = set([(a, b) for a in events for b in events if a.time < b.time and not set(
        [oi for oi in a.omap]).isdisjoint(set([oi for oi in b.omap]))])
    graph.add_edges_from(edges)

    otmap = {e: set([objects[oi].type for oi in e.omap]) for e in events}

    # event_objects = set([oi for e in events for oi in e.omap])
    # ovmap = {oi: objects[oi] for oi in event_objects}
    ovmap = objects

    eog = EventGraph(graph=graph, otmap=otmap, ovmap=ovmap)
    # nx.draw(graph, with_labels=True)
    # plt.show()
    return eog
