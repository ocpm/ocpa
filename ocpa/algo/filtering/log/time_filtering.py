from ocpa.objects.log.obj import OCEL
from ocpa.algo.filtering.log import case_filtering

def start(start, end, exec_start, exec_end):
    return (exec_start >= start) & (exec_start <= end)

def spanning(start, end, exec_start, exec_end):
    return ((exec_start <= start) & (exec_end >= start)) | ((exec_start <= end) & (exec_end >= end))

def extract_sublog(ocel,start,end,strategy):
    if strategy == extract_sublog_events:
        return extract_sublog_events(ocel,start,end)
    cases = []
    mapping_time = dict(zip(ocel.log["event_id"], ocel.log["event_timestamp"]))
    #id_index = list(ocel.log.columns.values).index("event_id")
    #id_time = list(ocel.log.columns.values).index("event_timestamp")
    #arr = ocel.log.to_numpy()
    for i in range(0,len(ocel.cases)):
        case = ocel.cases[i]
        exec_start = min([mapping_time[e] for e in case])
        exec_end = max([mapping_time[e]  for e in case])
        if strategy(start, end, exec_start, exec_end):
            cases+=[ocel.cases[i]]

    return case_filtering.filter_cases(ocel,cases)

def extract_sublog_events(ocel,start,end):
    events = []
    id_index = list(ocel.log.columns.values).index("event_id")
    id_time = list(ocel.log.columns.values).index("event_timestamp")
    arr = ocel.log.to_numpy()
    for line in arr:
        if start <= line[id_time] & line[id_time] <= end:
            events.append(line[id_index])
    new_ocel = ocel.copy()
    new_ocel.log = new_ocel.log[~new_ocel.log['event_id'].isin(events)]
    return new_ocel

