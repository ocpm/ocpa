import networkx as nx
from ocpa.objects.event_graph.obj import EventGraph
import matplotlib.pyplot as plt
import time

from itertools import combinations


def apply(ocel):
    events = [ocel.raw.events[ei] for ei in ocel.raw.events]
    objects = ocel.raw.objects
    graph = nx.DiGraph()
    st = time.time()
    graph.add_nodes_from(events)
    ct = time.time()
    print(ct-st)
    st = time.time()
    # edges = set([(a, b) for a in events for b in events if (a.time < b.time and not set(
    #     [oi for oi in a.omap]).isdisjoint(set([oi for oi in b.omap])))])

    edges = set()
    for a, b in combinations(events, 2):
        if a.time < b.time and not set([oi for oi in a.omap]).isdisjoint(set([oi for oi in b.omap])):
            edges.add((a, b))
    # set(edges)

    ct = time.time()
    print(ct-st)
    st = time.time()
    graph.add_edges_from(edges)
    ct = time.time()
    print(ct-st)
    st = time.time()
    otmap = {e: set([objects[oi].type for oi in e.omap]) for e in events}

    # event_objects = set([oi for e in events for oi in e.omap])
    # ovmap = {oi: objects[oi] for oi in event_objects}
    ovmap = objects

    eog = EventGraph(graph=graph, otmap=otmap, ovmap=ovmap)
    ct = time.time()
    print(ct-st)
    # nx.draw(graph, with_labels=True)
    # plt.show()
    return eog
