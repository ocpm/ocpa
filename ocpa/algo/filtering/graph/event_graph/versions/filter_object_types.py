from ocpa.objects.oc_petri_net.obj import Subprocess, ObjectCentricPetriNet
from copy import deepcopy
from ocpa.objects.graph.correlated_event_graph.obj import CorrelatedEventGraph


# def apply(ocpn: ObjectCentricPetriNet, cegs, parameters):
#     selected_object_types = ocpn.object_types

#     new_cegs = set()
#     for ceg in cegs:
#         graph = ceg.graph
#         otmap = ceg.otmap
#         ovmap = ceg.ovmap

#         remove = [e for e in graph.nodes if otmap[e].isdisjoint(
#             set(selected_object_types))]
#         new_graph = ceg.graph.copy()
#         new_graph.remove_nodes_from(remove)

#         new_ceg = CorrelatedEventGraph(ceg.name, new_graph, otmap, ovmap)
#         new_cegs.add(new_ceg)

#     return new_cegs

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
