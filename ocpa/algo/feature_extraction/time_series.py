from ocpa.algo.filtering.log import time_filtering
import ocpa.algo.feature_extraction.factory as feature_extraction
import numpy as np
def construct_time_series(ocel, w, feat_events, feat_cases, f_in = time_filtering.start):
    #feat_events and feat_cases are tuples of an aggregation funciton and a feature from feature_extraction....
    l_start = ocel.log["event_timestamp"].min()
    l_end = ocel.log["event_timestamp"].max()
    m = int(1  + ((l_end - l_start) / w))
    s = {}
    for i in range(0,m):
        start = l_start + i*w
        end = l_start +(i+1)*w
        sublog = time_filtering.extract_sublog(ocel,start,end,f_in)
        if len(sublog.log)==0:
            for feat in feat_events:
                if feat not in s.keys():
                    s[feat] = []
                s[feat].append(0)
            for feat in feat_cases:
                if feat not in s.keys():
                    s[feat] = []
                s[feat].append(0)
            continue
        feature_storage = feature_extraction.apply(sublog,[f[1] for f in feat_events],[f[1] for f in feat_cases])
        events = []
        for g in feature_storage.feature_graphs:
            for n in g.nodes:
                events.append(n.attributes)
        for feat in feat_events:
            v = feat[0]([e[feat[1]]for e in events])
            if feat not in s.keys():
                s[feat] = []
            s[feat].append(v)
        for feat in feat_cases:
            v = feat[0]([c.attributes[feat[1]]for c in feature_storage.feature_graphs])
            if feat not in s.keys():
                s[feat] = []
            s[feat].append(v)
    for k in s.keys():
        s[k] = np.asarray(s[k])
    return s
