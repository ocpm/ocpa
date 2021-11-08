from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet, Subprocess
from ocpa.objects.correlated_event_graph.obj import CorrelatedEventGraph


# def apply(ocpn: ObjectCentricPetriNet, cegs, parameters):
#     selected_transitions = ocpn.transitions

#     selected_transition_labels = [t.name for t in selected_transitions]

#     new_cegs = set()
#     for ceg in cegs:
#         graph = ceg.graph
#         otmap = ceg.otmap
#         ovmap = ceg.ovmap

#         # TODO: currently assume activities are unique.
#         remove = [
#             event for event in graph.nodes if event.act not in selected_transition_labels]

#         new_graph = ceg.graph.copy()

#         new_graph.remove_nodes_from(remove)

#         new_ceg = CorrelatedEventGraph(ceg.name, new_graph, otmap, ovmap)
#         new_cegs.add(new_ceg)

#     return new_cegs

def apply(sp: Subprocess, ceg, parameters):

    selected_transition_labels = [t.name for t in sp.transitions]
    graph = ceg.graph
    otmap = ceg.otmap
    ovmap = ceg.ovmap

    # TODO: currently assume activities are unique.
    transition_remove = [
        event for event in graph.nodes if event.act not in selected_transition_labels]
    ot_remove = [e for e in graph.nodes if otmap[e].isdisjoint(
        set(sp.object_types))]
    remove = set(transition_remove+ot_remove)

    new_graph = ceg.graph.copy()

    new_graph.remove_nodes_from(remove)

    new_ceg = CorrelatedEventGraph(ceg.name, new_graph, otmap, ovmap)

    return new_ceg
