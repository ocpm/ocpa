#This is a loose collection of possible feature functions on the process execution level. the submodule of
#event_based_features contains a plethora of feature function on the event level. Several of these, such as
#as remaining time, are generalizaitons of the process execution features

def number_of_events(case,ocel,params):
    return len(case.nodes)

def number_of_ending_events(case,ocel,params):
    return len([n for n in case.nodes if len(list(case.out_edges(n)))==0 ])

def throughput_time(case,ocel,params):
    events = list(case.nodes)
    timestamps = [ocel.get_value(e,"event_timestamp") for e in events]
    #event_log = ocel.log.loc[events]
    return (max(timestamps) - min(timestamps)).total_seconds()
    #return (event_log["event_timestamp"].max()-event_log["event_timestamp"].min()).total_seconds()

def execution(case,ocel,params):
    return 1

def number_of_objects(case, ocel,params):
    events = list(case.nodes)
    objects = set()
    for e in events:
        objects= objects.union(set(ocel.get_value(e, "event_objects")))
    return len(objects)

def unique_activites(case, ocel,params):
    events = list(case.nodes)
    activities = set([ocel.get_value(e,"event_activity") for e in events])
    return len(activities)

def number_of_starting_events(case,ocel,params):
    return len([n for n in case.nodes if len(list(case.in_edges(n)))==0 ])

def delta_last_event(case,ocel,params):
    events = list(case.nodes)
    timestamps = [ocel.get_value(e,"event_timestamp") for e in events]
    timestamps.sort(reverse=True)
    if len(timestamps)>1:
        return (timestamps[0] - timestamps[1]).total_seconds()
    else:
        return 0


def service_time(case,ocel, params):
    #give the starttimestamp attribute name in params
    events = list(case.nodes)
    timestamps = [ocel.get_value(e, "event_timestamp") for e in events]
    start_timestamps = [ocel.get_value(e, params[0]) for e in events]
    return sum([(timestamps[i]-start_timestamps[i]).total_seconds() for i in range(0, len(timestamps)) if start_timestamps[i]])

def avg_service_time(case,ocel, params):
    #give the starttimestamp attribute name in params
    events = list(case.nodes)
    timestamps = [ocel.get_value(e, "event_timestamp") for e in events]
    start_timestamps = [ocel.get_value(e, params[0]) for e in events]
    diffs = [(timestamps[i] - start_timestamps[i]).total_seconds() for i in range(0, len(timestamps)) if start_timestamps[i]]
    if len(diffs) == 0:
        return 0
    return sum(diffs)/len(diffs)
