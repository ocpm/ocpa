from ocpa.objects.oc_petri_net.obj import EnhancedObjectCentricPetriNet
from ocpa.algo.enhancement.token_replay_based_performance import algorithm as performance_factory


def apply(ocpn, ocel, parameters=None) -> EnhancedObjectCentricPetriNet:
    diag = performance_factory.apply(ocpn, ocel, parameters=parameters)
    eocpn = EnhancedObjectCentricPetriNet(ocpn, diag)
    return eocpn
