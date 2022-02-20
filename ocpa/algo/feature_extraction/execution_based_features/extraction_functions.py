def number_of_events(case,ocel):
    return len(case.nodes)

def number_of_ending_events(case,ocel):
    return len([n for n in case.nodes if len(list(case.out_edges(n)))==0 ])

def throughput_time(case,ocel):
    events = list(case.nodes)
    timestamps = [ocel.get_value(e,"event_timestamp") for e in events]
    #event_log = ocel.log.loc[events]
    return (max(timestamps) - min(timestamps)).total_seconds()
    #return (event_log["event_timestamp"].max()-event_log["event_timestamp"].min()).total_seconds()

def execution(case,ocel):
    return 1