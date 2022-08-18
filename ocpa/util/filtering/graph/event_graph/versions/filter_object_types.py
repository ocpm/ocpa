from ocpa.objects.oc_petri_net.obj import Subprocess
from ocpa.objects.graph.correlated_event_graph.obj import CorrelatedEventGraph


def apply(sp: Subprocess, ceg, parameters):
    graph = ceg.graph
    otmap = ceg.otmap
    ovmap = ceg.ovmap
    remove = [e for e in graph.nodes if otmap[e].isdisjoint(
        set(sp.object_types))]
    new_graph = ceg.graph.copy()
    new_graph.remove_nodes_from(remove)

    new_ceg = CorrelatedEventGraph(ceg.name, new_graph, otmap, ovmap)

    return new_ceg
