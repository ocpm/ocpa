import time

import ocpa.algo.predictive_monitoring.event_based_features.extraction_functions as event_features
import ocpa.algo.predictive_monitoring.execution_based_features.extraction_functions as execution_features
from ocpa.algo.predictive_monitoring.obj import Feature_Storage

EVENT_BASED = "event_based"
EXECUTION_BASED = "execution_based"

EVENT_NUM_OF_OBJECTS = "num_objects"
EVENT_ACTIVITY = "event_activity"
EVENT_SERVICE_TIME = "event_service"
EVENT_IDENTITY = "event_identity"
EVENT_TYPE_COUNT = "event_type_count"
EVENT_PRECEDING_ACTIVITES = "event_preceding_activities"
EVENT_PREVIOUS_ACTIVITY_COUNT = "event_previous_activity_count"
EVENT_CURRENT_ACTIVITIES = "event_current_activities"
EVENT_AGG_PREVIOUS_CHAR_VALUES = "event_aggregate_previous_char"
EVENT_PRECEDING_CHAR_VALUES = "event_preceding_char_values"
EVENT_CHAR_VALUE = "event_char_value"
EVENT_CURRENT_RESOURCE_WORKLOAD = "event_current_resource_workload"
EVENT_CURRENT_TOTAL_WORKLOAD = "event_current_total_workload"
EVENT_RESOURCE = "event_resource"
EVENT_CURRENT_TOTAL_OBJECT_COUNT = "event_current_total_object_count"
EVENT_PREVIOUS_OBJECT_COUNT = "event_previous_object_count"
EVENT_PREVIOUS_TYPE_COUNT = "event_previous_type_count"
EVENT_OBJECTS = "event_objects"
EVENT_EXECUTION_DURATION = "event_execution_time"
EVENT_ELAPSED_TIME = "event_elapsed_time"
EVENT_REMAINING_TIME = "event_remaining_time"
EVENT_DURATION = "event_duration"
EVENT_FLOW_TIME = "event_flow_time"
EVENT_SYNCHRONIZATION_TIME = "event_synchronization_time"
EVENT_SOJOURN_TIME = "event_sojourn_time"
EVENT_WAITING_TIME = "event_waiting_time"
EVENT_POOLING_TIME = "event_pooling_time"
EVENT_LAGGING_TIME = "event_lagging_time"

EXECUTION_NUM_OF_EVENTS = "num_events"
EXECUTION_NUM_OF_END_EVENTS = "num_end_events"
EXECUTION_THROUGHPUT = "exec_throughput"
EXECUTION_IDENTITY = "exec_identity"
EXECUTION_NUM_OBJECT = "exec_objects"
EXECUTION_UNIQUE_ACTIVITIES = "exec_uniq_activities"
EXECUTION_NUM_OF_STARTING_EVENTS = "exec_num_start_events"
EXECUTION_LAST_EVENT_TIME_BEFORE = "exec_last_event"
EXECUTION_FEATURE = "exec_feature"
EXECUTION_SERVICE_TIME = "exec_service_time"
EXECUTION_AVG_SERVICE_TIME = "exec_avg_service_time"


VERSIONS = {
    EVENT_BASED: {EVENT_NUM_OF_OBJECTS: event_features.number_of_objects,
                  EVENT_ACTIVITY: event_features.event_activity,
                  EVENT_SERVICE_TIME: event_features.service_time,
                  EVENT_IDENTITY: event_features.event_identity,
                  EVENT_TYPE_COUNT: event_features.event_type_count,
                  EVENT_PRECEDING_ACTIVITES: event_features.preceding_activities,
                  EVENT_PREVIOUS_ACTIVITY_COUNT: event_features.previous_activity_count,
                  EVENT_CURRENT_ACTIVITIES: event_features.current_activities,
                  EVENT_AGG_PREVIOUS_CHAR_VALUES: event_features.agg_previous_char_values,
                  EVENT_PRECEDING_CHAR_VALUES: event_features.preceding_char_values,
                  EVENT_CHAR_VALUE: event_features.characteristic_value,
                  EVENT_CURRENT_RESOURCE_WORKLOAD: event_features.current_resource_workload,
                  EVENT_CURRENT_TOTAL_WORKLOAD: event_features.current_total_workload,
                  EVENT_RESOURCE: event_features.event_resource,
                  EVENT_CURRENT_TOTAL_OBJECT_COUNT: event_features.current_total_object_count,
                  EVENT_PREVIOUS_OBJECT_COUNT: event_features.previous_object_count,
                  EVENT_PREVIOUS_TYPE_COUNT: event_features.previous_type_count,
                  EVENT_OBJECTS: event_features.event_objects,
                  EVENT_EXECUTION_DURATION: event_features.execution_duration,
                  EVENT_ELAPSED_TIME: event_features.elapsed_time,
                  EVENT_REMAINING_TIME: event_features.remaining_time,
                  EVENT_DURATION: event_features.event_duration,
                  EVENT_LAGGING_TIME: event_features.lagging_time,
                  EVENT_POOLING_TIME: event_features.pooling_time,
                  EVENT_WAITING_TIME: event_features.waiting_time,
                  EVENT_SOJOURN_TIME: event_features.sojourn_time,
                  EVENT_SYNCHRONIZATION_TIME: event_features.sojourn_time,
                  EVENT_FLOW_TIME: event_features.flow_time


                  },
    EXECUTION_BASED: {EXECUTION_NUM_OF_EVENTS: execution_features.number_of_events,
                      EXECUTION_NUM_OF_END_EVENTS: execution_features.number_of_ending_events,
                      EXECUTION_THROUGHPUT: execution_features.throughput_time,
                      EXECUTION_IDENTITY: execution_features.execution,
                      EXECUTION_NUM_OBJECT: execution_features.number_of_objects,
                      EXECUTION_UNIQUE_ACTIVITIES: execution_features.unique_activites,
                      EXECUTION_NUM_OF_STARTING_EVENTS: execution_features.number_of_starting_events,
                      EXECUTION_LAST_EVENT_TIME_BEFORE: execution_features.delta_last_event,
                      EXECUTION_SERVICE_TIME: execution_features.service_time,
                      EXECUTION_AVG_SERVICE_TIME: execution_features.avg_service_time
                      }
}


def apply(ocel, event_based_features=[], execution_based_features=[], event_attributes=[], event_object_attributes=[], execution_object_attributes=[]):
    '''
    Creates a :class:`Feature Storage object <ocpa.algo.predictive_monitoring.obj.Feature_Storage>` from the object-centric
    event log considering the desired features. Features are passed as a list of Tuples, containing first the function
    to calculate the feature and second a tuple of parameter values (can be empty). The feature functions need to have
    a signature of (event_id (int), :class:`ocel <ocpa.objects.log.ocel.OCEL>`, parameters (Tuple)) for event-based
    features or (case (int), :class:`ocel <ocpa.objects.log.ocel.OCEL>`, parameters (Tuple)) for execution-based features.
    A set of predefined feature functions can be found in :mod:`event-based features <ocpa.algo.predictive_monitoring.event_based_features>`
    and :mod:`event-based features <ocpa.algo.predictive_monitoring.execution_based_features>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param event_based_features: list of event-based features. Each feature is a tuple of the function and parameter tuple
    :type event_based_features: Tuple(function, Tuple())

    :param execution_based_features: list of execution-based features. Each feature is a tuple of the function and parameter tuple
    :type execution_based_features: Tuple(function, Tuple())

    :param event_attributes: List of event attributes to be added to an event's features.
    :type event_attributes: str

    :param event_object_attributes: To be added in future
    :param execution_object_attributes: To be added in future

    :return: Feature Storage
    :rtype: :class:`Feature Storage <ocpa.algo.predictive_monitoring.obj.Feature_Storage>`

    '''

    s_time = time.time()
    ocel.log.log["event_objects"] = ocel.log.log.apply(
        lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]], axis=1)
    ocel.log.create_efficiency_objects()
    feature_storage = Feature_Storage(
        event_features=event_based_features, execution_features=execution_based_features, ocel=ocel)
    object_f_time = time.time()-s_time
    id = 0
    subgraph_time = 0
    execution_time = 0
    nodes_time = 0
    adding_time = 0
    for case in ocel.process_executions:
        s_time = time.time()
        case_graph = ocel.graph.eog.subgraph(case)
        feature_graph = Feature_Storage.Feature_Graph(
            case_id=id, graph=case_graph, ocel=ocel)
        subgraph_time += time.time() - s_time
        s_time = time.time()
        for execution_feature in execution_based_features:
            execution_function, params = execution_feature
            feature_graph.add_attribute(
                execution_feature, VERSIONS[EXECUTION_BASED][execution_function](case_graph, ocel, params))
            for (object_type, attr, fun) in execution_object_attributes:
                # TODO add object frame
                feature_graph.add_attribute(
                    object_type+"_"+attr+fun.__name__, fun([object_type[attr]]))
        execution_time += time.time() - s_time
        s_time = time.time()
        for node in feature_graph.nodes:
            for event_feature in event_based_features:
                event_function, params = event_feature
                node.add_attribute(
                    event_feature, VERSIONS[EVENT_BASED][event_function](node, ocel, params))
            for attr in event_attributes:
                node.add_attribute(attr, ocel.get_value(node.event_id, attr))
                # node.add_attribute(attr,ocel.log.loc[node.event_id][attr])
            for (object_type, attr, fun) in event_object_attributes:
                # TODO add object frame
                feature_graph.add_attribute(
                    object_type+"_"+attr+fun.__name__, fun([object_type[attr]]))
        nodes_time += time.time() - s_time
        s_time = time.time()
        feature_storage.add_feature_graph(feature_graph)
        adding_time += time.time() - s_time
        id += 1
    del ocel.log.log["event_objects"]
    # print("___")
    #print("Execution time "+str(execution_time))
    #print("Node Features " + str(nodes_time))
    #print("Adding Features " + str(adding_time))
    #print("Subgraph Features " + str(subgraph_time))
    #print("prep time " + str(object_f_time))
    return feature_storage
