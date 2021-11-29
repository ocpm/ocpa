import ocpa.algo.feature_extraction.event_based_features.extraction_functions as event_features
import ocpa.algo.feature_extraction.execution_based_features.extraction_functions as execution_features
from ocpa.algo.feature_extraction.obj import Feature_Storage

EVENT_BASED = "event_based"
EXECUTION_BASED = "execution_based"

EVENT_NUM_OF_OBJECTS ="num_objects"
EXECUTION_NUM_OF_EVENTS ="num_events"


ANNOTATED_WITH_DIAGNOSTICS = "annotated_with_diagnostics"

VERSIONS = {
    EVENT_BASED: {EVENT_NUM_OF_OBJECTS:event_features.number_of_objects},
    EXECUTION_BASED: {EXECUTION_NUM_OF_EVENTS:execution_features.number_of_events}
}




def apply(ocel, event_based_features =[], execution_based_features = []):
    ocel.log["event_objects"] = ocel.log.apply(lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]], axis=1)
    feature_storage = Feature_Storage(event_features=event_based_features,execution_features=execution_based_features,ocel = ocel)
    id =0
    for case in ocel.cases:
        case_graph = ocel.eog.subgraph(case)
        feature_graph = Feature_Storage.Feature_Graph(case_id=0, graph=case_graph, ocel=ocel)
        for execution_feature in execution_based_features:
            feature_graph.add_attributes(execution_feature,VERSIONS[EXECUTION_BASED][execution_feature](case_graph,ocel))
        for node in feature_graph.nodes:
            for event_feature in event_based_features:
                node.add_attributes(event_feature,VERSIONS[EVENT_BASED][event_feature](node,ocel))
        feature_storage.add_feature_graph(feature_graph)
        id+=1

    del ocel.log["event_objects"]
    return feature_storage