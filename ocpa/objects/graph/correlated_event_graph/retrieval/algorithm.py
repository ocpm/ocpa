import networkx as nx
from ocpa.objects.graph.correlated_event_graph.obj import CorrelatedEventGraph


def apply(event_graph):
    otmap = event_graph.otmap
    ovmap = event_graph.ovmap
    correlated_graphs = nx.weakly_connected_components(event_graph.graph)
    cegs = set()
    for comp in correlated_graphs:
        cgraph = event_graph.graph.subgraph(comp)
        cgraph = nx.transitive_reduction(cgraph)
        events = list(cgraph.nodes)
        cotmap = {e: otmap[e] for e in events}
        event_objects = set([oi for e in events for oi in e.omap])
        covmap = {oi: ovmap[oi] for oi in event_objects}
        ceg = CorrelatedEventGraph(event_graph.name, cgraph, cotmap, covmap)
        cegs.add(ceg)
    return cegs
