import ocpa.algo.feature_extraction.event_based_features.extraction_functions as event_features
import ocpa.algo.feature_extraction.execution_based_features.extraction_functions as execution_features
from ocpa.algo.feature_extraction.obj import Feature_Storage

EVENT_BASED = "event_based"
EXECUTION_BASED = "execution_based"

EVENT_NUM_OF_OBJECTS ="num_objects"
EXECUTION_NUM_OF_EVENTS ="num_events"
EXECUTION_NUM_OF_END_EVENTS = "num_end_events"



VERSIONS = {
    EVENT_BASED: {EVENT_NUM_OF_OBJECTS:event_features.number_of_objects},
    EXECUTION_BASED: {EXECUTION_NUM_OF_EVENTS:execution_features.number_of_events,
                      EXECUTION_NUM_OF_END_EVENTS:execution_features.number_of_ending_events}
}




def apply(ocel, event_based_features =[], execution_based_features = [], event_attributes = [],event_object_attributes = [],execution_object_attributes = []):
    ocel.log["event_objects"] = ocel.log.apply(lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]], axis=1)
    feature_storage = Feature_Storage(event_features=event_based_features,execution_features=execution_based_features,ocel = ocel)
    id =0
    for case in ocel.cases:
        case_graph = ocel.eog.subgraph(case)
        feature_graph = Feature_Storage.Feature_Graph(case_id=0, graph=case_graph, ocel=ocel)
        for execution_feature in execution_based_features:
            feature_graph.add_attribute(execution_feature,VERSIONS[EXECUTION_BASED][execution_feature](case_graph,ocel))
            for (object_type, attr, fun) in execution_object_attributes:
                #TODO add object frame
                feature_graph.add_attribute(object_type+"_"+attr+fun.__name__, fun([object_type[attr]]))
        for node in feature_graph.nodes:
            for event_feature in event_based_features:
                node.add_attribute(event_feature,VERSIONS[EVENT_BASED][event_feature](node,ocel))
            for attr in event_attributes:
                node.add_attribute(attr,ocel.log.loc[node.event_id][attr])
            for (object_type, attr, fun) in event_object_attributes:
                #TODO add object frame
                feature_graph.add_attribute(object_type+"_"+attr+fun.__name__, fun([object_type[attr]]))
        feature_storage.add_feature_graph(feature_graph)
        id+=1

    del ocel.log["event_objects"]
    return feature_storage