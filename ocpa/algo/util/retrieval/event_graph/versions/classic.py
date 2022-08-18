import networkx as nx
from ocpa.objects.graph.event_graph.obj import EventGraph
# import matplotlib.pyplot as plt
import time


def apply(ocel, parameters=None):
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

    # old_edges = set()
    # for a, b in combinations(events, 2):
    #     if a.time < b.time and not set([oi for oi in a.omap]).isdisjoint(set([oi for oi in b.omap])):
    #         old_edges.add((a, b))
    # ct = time.time()
    # print(ct-st)

    # st = time.time()
    # edges = set()
    # found = set()
    # for a in events:
    #     for b in events:
    #         for oi in a.omap:
    #             if oi in b.omap:
    #                 edges.add((a, b))
    #                 found.add(oi)
    #                 continue
    #         if found == set(a.omap):
    #             found = set()
    #             break
    # ct = time.time()
    # print(ct-st)

    st = time.time()
    edges = set()

    for i in range(len(events)):
        found = set()
        a = events[i]
        for j in range(i+1, len(events), 1):
            b = events[j]
            for oi in a.omap:
                if oi in b.omap:
                    edges.add((a, b))
                    found.add(oi)
            if found == set(a.omap):
                break
    ct = time.time()
    print(ct-st)
    # print(len(old_edges), len(edges))

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
    return eog
