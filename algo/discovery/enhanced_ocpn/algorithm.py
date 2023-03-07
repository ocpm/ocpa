from ocpa.objects.oc_petri_net.obj import EnhancedObjectCentricPetriNet
from ocpa.algo.enhancement.token_replay_based_performance import algorithm as performance_factory
import ocpa.algo.util.retrieval.event_graph.algorithm as event_graph_factory
import ocpa.algo.util.retrieval.correlated_event_graph.algorithm as correlated_event_graph_factory


def apply(ocpn, ocel, parameters=None) -> EnhancedObjectCentricPetriNet:
    diag = performance_factory.apply(ocpn, ocel, parameters=parameters)
    eog = event_graph_factory.apply(ocel, parameters=None)
    cegs = correlated_event_graph_factory.apply(eog)
    behavior = []
    for ceg in cegs:
        bv = ceg.get_sequence()
        if bv not in behavior:
            behavior.append(bv)
    eocpn = EnhancedObjectCentricPetriNet(ocpn, behavior, diag)
    return eocpn
