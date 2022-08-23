from ocpa.algo.util.filtering.log import time_filtering
import ocpa.algo.predictive_monitoring.factory as feature_extraction
import numpy as np
import time
def construct_time_series(ocel, w, feat_events, feat_cases, f_in = time_filtering.start):
    '''
    Constructs a time series from an object-centric event log.
    :param ocel: Object-Centric Event Log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param w: window size
    :type w: time.timedelta

    :param feat_events: Features to be calculated on an event level. Tuple of a function to aggregate the values for a window and the feature function. For the definition of a function please see :func:`feature extraction <ocpa.algo.predictive_monitoring.factory.apply>`
    :type feat_events: Tuple(func, Tuple(func, Tuple()))

    :param feat_cases: Features to be calculated on a process_execution (case) level. Tuple of a function to aggregate the values for a window and the feature function. For the definition of a function please see :func:`feature extraction <ocpa.algo.predictive_monitoring.factory.apply>`
    :type feat_events: Tuple(func, Tuple(func, Tuple()))

    :param f_in: Function to assign events to time windows. Possible functions can be found in :obj:`time_filtering <ocpa.algo.filtering.log.time_filtering>`:, e.g., :func:`by start timestamp of the process execution <ocpa.algo.filtering.log.time_filtering.start>`:
    :type f_in: func

    :return: time series as list of dictionaries of values, list of time stamps for each index
    :rtype: list(dict))

    '''
    #feat_events and feat_cases are tuples of an aggregation funciton and a feature from predictive_monitoring....
    time_index = []
    l_start = ocel.log["event_timestamp"].min()
    l_end = ocel.log["event_timestamp"].max()
    m = int(1  + ((l_end - l_start) / w))
    s = {}
    extract_sublog = 0
    feature_time = 0
    print(f_in)
    for i in range(0,m):
        start = l_start + i*w
        end = l_start +(i+1)*w
        time_index.append(start)
        s_time = time.time()
        sublog = time_filtering.extract_sublog(ocel, start, end, f_in)
        extract_sublog += time.time()-s_time
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
        s_time = time.time()
        feature_storage = feature_extraction.apply(sublog,[f[1] for f in feat_events],[f[1] for f in feat_cases])
        feature_time += time.time() - s_time
        events = []
        for g in feature_storage.feature_graphs:
            for n in g.nodes:
                events.append(n.attributes)
        for feat in feat_events:
            v = feat[0]([e[feat[1]]for e in events if e[feat[1]]])
            if feat not in s.keys():
                s[feat] = []
            s[feat].append(v)
        for feat in feat_cases:
            v = feat[0]([c.attributes[feat[1]] for c in feature_storage.feature_graphs if c.attributes[feat[1]]])
            if feat not in s.keys():
                s[feat] = []
            s[feat].append(v)
        print(str(i)+"/"+str(m)+ " windows done")
    print(f_in)
    print("Extraction time: "+str(extract_sublog))
    print("Feature time: " + str(feature_time))
    for k in s.keys():
        s[k] = np.asarray(s[k])
    return s, time_index
