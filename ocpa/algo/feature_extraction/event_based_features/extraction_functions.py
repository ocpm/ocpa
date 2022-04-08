#Control Flow
def current_activities(node, ocel, params):
    return

def preceding_activities(node, ocel, params):
    return

def previous_activity_count(node,ocel,params):
    return

def event_activity(node, ocel, params):
    return

#data flow
def agg_previous_char_values(node, ocel, params):
    return

def preceding_char_values(node,ocel,params):
    return

def characteristic_value(node, ocel, params):
    return

#resource
def current_resource_workload(node, ocel, params):
    return

def current_total_workload(node, ocel, params):
    return

def event_resource(node, ocel, params):
    return


#performance
def execution_duration(node, ocel, params):
    return

def elapsed_time(node, ocel, params):
    return

def remaining_time(node, ocel, params):
    return

def flow_time(node, ocel, params):
    return

def synchronization_time(node, ocel, params):
    return

def sojourn_time(node, ocel, params):
    return

def pooling_time(node, ocel, params):
    return

def lagging_time(node, ocel, params):
    return

def service_time(node, ocel, params):
    start_column = params[0]
    activity = params[1]
    if ocel.get_value(node.event_id,"event_activity") == activity:
        return (ocel.get_value(node.event_id,"event_timestamp") - ocel.get_value(node.event_id,start_column)).total_seconds()
    else:
        return None

def waiting_time(node, ocel, params):
    return

#objects
def current_total_object_count(node, ocel, params):
    return

def previous_object_count(node, ocel, params):
    return

def previous_type_count(node, ocel, params):
    return

def event_objects(node, ocel, params):
    return

def number_of_objects(node,ocel, params):
    return len(ocel.get_value(node.event_id,"event_objects"))
    #return len(ocel.log.loc[node.event_id]["event_objects"])

def event_type_count(node, ocel, params):
    return len(ocel.get_value(node.event_id, params[0]))
    return


def event_identity(node,ocel, params):
    return 1
    #return len(ocel.log.loc[node.event_id]["event_objects"])



