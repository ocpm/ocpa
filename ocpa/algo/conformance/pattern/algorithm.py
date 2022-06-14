from ocpa.algo.conformance.pattern.versions import model_based
from ocpa.algo.conformance.pattern.versions import log_based
from ocpa.objects.graph.pattern_graph.obj import PatternGraph
from ocpa.objects.enhanced_oc_petri_net.obj import EnhancedObjectCentricPetriNet
from ocpa.objects.log.obj import ObjectCentricEventLog

MODEL_BASED = "model_based"
LOG_BASED = "log_based"

VERSIONS = {MODEL_BASED: model_based.apply, LOG_BASED: log_based.apply}


def apply(pg: PatternGraph, ocel: ObjectCentricEventLog, eocpn: EnhancedObjectCentricPetriNet, variant=LOG_BASED, parameters=None):
    return VERSIONS[variant](pg, ocel, eocpn, parameters=parameters)
