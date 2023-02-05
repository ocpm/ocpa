from ocpa.algo.enhancement.event_graph_based_performance.versions import perfectly_fitting, event_object_graph_based

PERFECTLY_FITTING = "perfectly_fitting"
EVENT_OBJECT_GRAPH = "event_object_graph_based"

VERSIONS = {
    PERFECTLY_FITTING: perfectly_fitting.apply,
    EVENT_OBJECT_GRAPH: event_object_graph_based.apply
}


def apply(ocel, variant=EVENT_OBJECT_GRAPH, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
