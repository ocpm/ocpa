import datetime
#helper functions:
def get_recent_events(event, case_index, ocel):
    case = ocel.process_executions[case_index]
    subset_events = []
    for e in case:
        if ocel.get_value(e, "event_timestamp") <= ocel.get_value(event, "event_timestamp"):
            subset_events.append(e)
    return subset_events

#Control Flow
def current_activities(node, ocel, params):
    #other current end activities (without finished events)
    act = params[0]
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for case in cases:
        c_res = 0
        recent_events = get_recent_events(e_id, case, ocel)
        subgraph = ocel.graph.eog.subgraph(recent_events)
        end_nodes = [n for n in subgraph.nodes if len(list(subgraph.out_edges(n)))==0 ]
        for e in end_nodes:
            if ocel.get_value(e,"event_activity") == act:
                c_res = 1
        value_array.append(c_res)

    return sum(value_array)/len(value_array)

def preceding_activities(node, ocel, params):
    act = params[0]
    e_id = node.event_id
    in_edges = ocel.graph.eog.in_edges(e_id)
    count = 0
    for (source,target) in in_edges:
        if ocel.get_value(source,"event_activity") == act:
            count+=1
    return count

def previous_activity_count(node,ocel,params):
    act = params[0]
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for c in cases:
        c_count = 0
        case = ocel.process_executions[c]
        for e in case:
            if ocel.get_value(e,"event_timestamp") > ocel.get_value(e_id,"event_timestamp"):
                continue
            else:
                if ocel.get_value(e,"event_activity") == act:
                    c_count+=1
        value_array += [c_count]

    return sum(value_array)/len(value_array)

def event_activity(node, ocel, params):
    act = params[0]
    if ocel.get_value(node.event_id,"event_activity") == act:
        return 1
    else:
        return 0

#data flow
def agg_previous_char_values(node, ocel, params):
    attribute = params[0]
    aggregation = params[1]
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for c in cases:
        c_vals = []
        events = get_recent_events(e_id, c, ocel)
        for e in events:
            c_vals.append(ocel.get_value(e,attribute))
        value_array += [aggregation(c_vals)]

    return sum(value_array) / len(value_array)
    return

def preceding_char_values(node,ocel,params):
    attribute = params[0]
    aggregation = params[1]
    e_id = node.event_id
    in_edges = ocel.graph.eog.in_edges(e_id)
    value_array = []
    for (source, target) in in_edges:
        v = ocel.get_value(source,attribute)
        value_array.append(v)

    return aggregation(value_array)
    return

def characteristic_value(node, ocel, params):
    attribute = params[0]
    return ocel.get_value(node.event_id,attribute)

#resource
#might have performance problems
def current_resource_workload(node, ocel, params):
    res_column = params[0]
    time_horizon = params[1]
    t_e = ocel.get_value(node.event_id,"event_timestamp")
    res = ocel.get_value(node.event_id,res_column)
    all_events = ocel.log["event_id"].tolist()
    result = 0
    for e in all_events:
        if t_e - time_horizon <= ocel.get_value(e,"event_timestamp") <= t_e:
            if ocel.get_value(e,res_column) == res:
                result += 1
    return result

def current_total_workload(node, ocel, params):
    res_column = params[0]
    time_horizon = params[1]
    t_e = ocel.get_value(node.event_id, "event_timestamp")
    all_events = ocel.log["event_id"].tolist()
    result = 0
    for e in all_events:
        if t_e - time_horizon <= ocel.get_value(e, "event_timestamp") <= t_e:
            result += 1
    return result


def event_resource(node, ocel, params):
    res_column = params[0]
    resource = params[1]
    if ocel.get_value(node.event_id, res_column) == resource:
        return 1
    else:
        return 0


#performance
def execution_duration(node, ocel, params):
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for case in cases:
        c_res = 0
        timestamps = [ocel.get_value(e,"event_timestamp") for e in ocel.process_executions[case]]
        duration = (max(timestamps) - min(timestamps)).total_seconds()
        value_array.append(duration)

    return sum(value_array) / len(value_array)

def elapsed_time(node, ocel, params):
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for case in cases:
        c_res = 0
        events = get_recent_events(e_id,case,ocel)
        timestamps = [ocel.get_value(e, "event_timestamp") for e in events]
        duration = (max(timestamps) - min(timestamps)).total_seconds()
        value_array.append(duration)

    return sum(value_array) / len(value_array)

def remaining_time(node, ocel, params):
    e_id = node.event_id
    value_array = []
    for case in [node.pexec_id]:
        c_res = 0
        prev_events = get_recent_events(e_id, case, ocel)
        following_events = [e for e in ocel.process_executions[case] if e not in prev_events]
        following_events.append(e_id)

        timestamps = [ocel.get_value(e, "event_timestamp") for e in following_events]
        duration = (max(timestamps) - min(timestamps)).total_seconds()
        value_array.append(duration)

    return sum(value_array) / len(value_array)


#These functions take pairs of activities as parameter that follow each other in the model
def flow_time(node, ocel, params):
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        #calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset]
        if len(end_timestamps) == 0:
            duration = 0
        else:
            duration = (ocel.get_value(node.event_id,"event_timestamp") - min(end_timestamps)).total_seconds()
        res.append(duration)

    return sum(res)/len(res)

def synchronization_time(node, ocel, params):
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        # calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset]
        duration = 0
        if len(end_timestamps) == 0:
            duration = 0
        else:
            duration = (max(end_timestamps) - min(end_timestamps)).total_seconds()
        res.append(duration)

    return sum(res) / len(res)

def sojourn_time(node, ocel, params):
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        # calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset]
        if len(end_timestamps) == 0:
            duration = 0
        else:
            duration = (ocel.get_value(node.event_id,"event_timestamp") - max(end_timestamps)).total_seconds()
        res.append(duration)

    return sum(res) / len(res)

def waiting_time(node,ocel, params):
    start_column = params[0]
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        # calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset]
        if len(end_timestamps) == 0:
            duration = 0
        else:
            duration = (ocel.get_value(node.event_id, start_column) - max(end_timestamps)).total_seconds()
        res.append(duration)

    return sum(res) / len(res)

def pooling_time(node, ocel, params):
    object_type = params[0]
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        # calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset if ocel.get_value(e,object_type)]
        if len(end_timestamps) == 0:
            duration = 0
        else:
            duration = (max(end_timestamps) - min(end_timestamps)).total_seconds()
        res.append(duration)

    return sum(res) / len(res)

def lagging_time(node, ocel, params):
    object_type = params[0]
    cases = ocel.process_execution_mappings[node.event_id]
    res = []
    for case in cases:
        in_edges = ocel.graph.eog.subgraph(ocel.process_executions[case]).in_edges(node.event_id)
        preset = [source for (source, target) in in_edges]
        # calculate measure
        end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset]
        if len(end_timestamps) == 0:
            duration = 0
        else:
            ot_maxs = []
            for ot in ocel.object_types:
                ot_end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset if ocel.get_value(e, ot)]
                ot_maxs.append(max(ot_end_timestamps))
            ot_end_timestamps = [ocel.get_value(e, "event_timestamp") for e in preset if
                                 ocel.get_value(e, object_type)]
            duration = (max(ot_end_timestamps) - min(ot_maxs)).total_seconds()
        res.append(duration)

    return sum(res) / len(res)

def service_time(node, ocel, params):
    start_column = params[0]
    return (ocel.get_value(node.event_id,"event_timestamp") - ocel.get_value(node.event_id,start_column)).total_seconds()


#objects
def current_total_object_count(node, ocel, params):
    time_horizon = params[0]
    t_e = ocel.get_value(node.event_id, "event_timestamp")
    all_events = ocel.log["event_id"].tolist()
    all_obs = set()
    for e in all_events:
        if t_e - time_horizon <= ocel.get_value(e, "event_timestamp") <= t_e:
            all_obs = all_obs.union(set(ocel.get_value(e,"event_objects")))
    return len(list(all_obs))

def previous_object_count(node, ocel, params):
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for c in cases:
        all_obs = set()
        events = get_recent_events(e_id, c, ocel)
        for e in events:
            all_obs = all_obs.union(set(ocel.get_value(e,"event_objects")))
        value_array += [len(list(all_obs))]

    return sum(value_array) / len(value_array)

def previous_type_count(node, ocel, params):
    t = params[0]
    e_id = node.event_id
    cases = ocel.process_execution_mappings[e_id]
    value_array = []
    for c in cases:
        all_obs = set()
        events = get_recent_events(e_id, c, ocel)
        for e in events:
            obs = ocel.get_value(e, "event_objects")
            for o in obs:
                (ot, ob_i) = o
                if ot == t:
                    all_obs.add(o)
        value_array += [len(list(all_obs))]

    return sum(value_array) / len(value_array)


def event_objects(node, ocel, params):
    ob = params[0]
    if ob in ocel.get_value(node.event_id,"event_objects"):
        return 1
    else:
        return 0

def number_of_objects(node,ocel, params):
    return len(ocel.get_value(node.event_id,"event_objects"))
    #return len(ocel.log.loc[node.event_id]["event_objects"])

def event_type_count(node, ocel, params):
    return len(ocel.get_value(node.event_id, params[0]))
    return


def event_identity(node,ocel, params):
    return 1
    #return len(ocel.log.loc[node.event_id]["event_objects"])



