from ocpa.algo.enhancement.event_graph_based_performance.versions import event_object_graph_based

EVENT_OBJECT_GRAPH = "event_object_graph_based"

VERSIONS = {
    EVENT_OBJECT_GRAPH: event_object_graph_based.apply
}


def apply(ocel, variant=EVENT_OBJECT_GRAPH, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
