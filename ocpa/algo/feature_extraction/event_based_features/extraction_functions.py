
def number_of_objects(node,ocel, params):
    return len(ocel.get_value(node.event_id,"event_objects"))
    #return len(ocel.log.loc[node.event_id]["event_objects"])

def service_time(node, ocel, params):
    start_column = params[0]
    activity = params[1]
    if ocel.get_value(node.event_id,"event_activity") == activity:
        return (ocel.get_value(node.event_id,"event_timestamp") - ocel.get_value(node.event_id,start_column)).total_seconds()
    else:
        return None

def event_identity(node,ocel, params):
    return 1
    #return len(ocel.log.loc[node.event_id]["event_objects"])


