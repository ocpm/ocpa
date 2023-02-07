from ocpa.algo.util.util import AGG_MAP


def apply(ocel, parameters):
    if 'measure' in parameters:
        measure = parameters['measure']
    else:
        raise ValueError('Specify a performance measure in parameters')
    if 'activity' in parameters:
        act = parameters['activity']
    else:
        raise ValueError('Specify an activity in parameters')

    if 'object_type' in parameters:
        ot = parameters['object_type']
    else:
        ot = None

    if 'aggregation' in parameters:
        agg = parameters['aggregation']
    else:
        raise ValueError('Specify an aggregation function in parameters')

    if measure == 'flow':
        return AGG_MAP[agg](flow_time(ocel, act))

    if measure == 'sojourn':
        return AGG_MAP[agg](sojourn_time(ocel, act))

    if measure == 'syncronization':
        return AGG_MAP[agg](synchronization_time(ocel, act))

    if measure == 'pooling':
        if ot is None:
            raise ValueError('Specify an object type in parameters')
        return AGG_MAP[agg](pooling_time(ocel, act, ot))

    if measure == 'lagging':
        if ot is None:
            raise ValueError('Specify an object type in parameters')
        return AGG_MAP[agg](lagging_time(ocel, act, ot))

    if measure == 'readying':
        if ot is None:
            raise ValueError('Specify an object type in parameters')
        return AGG_MAP[agg](readying_time(ocel, act, ot))

    if measure == 'object_freq':
        if ot is None:
            raise ValueError('Specify an object type in parameters')
        return AGG_MAP[agg](object_freq(ocel, act, ot))


def flow_time(ocel, act):
    flow_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                duration = (ocel.get_value(
                    node, "event_timestamp") - min(end_timestamps)).total_seconds()
            flow_times.append(duration)
    return flow_times


def synchronization_time(ocel, act):
    sync_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                duration = (max(end_timestamps) -
                            min(end_timestamps)).total_seconds()
            sync_times.append(duration)
    return sync_times


def sojourn_time(ocel, act):
    sojourn_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                duration = (ocel.get_value(node, "event_timestamp") -
                            max(end_timestamps)).total_seconds()
            sojourn_times.append(duration)
    return sojourn_times


def pooling_time(ocel, act, ot):
    pooling_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                ot_end_timestamps = [ocel.get_value(
                    e, "event_timestamp") for e in preset if len(ocel.get_value(e, ot)) > 0]
                duration = (max(ot_end_timestamps) -
                            min(ot_end_timestamps)).total_seconds()
            pooling_times.append(duration)
    return pooling_times


def lagging_time(ocel, act, ot):
    lagging_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                ot_end_timestamps = [ocel.get_value(
                    e, "event_timestamp") for e in preset if len(ocel.get_value(e, ot)) > 0]
                duration = (max(ot_end_timestamps) -
                            min(end_timestamps)).total_seconds()
            lagging_times.append(duration)
    return lagging_times


def readying_time(ocel, act, ot):
    readying_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            end_timestamps = [ocel.get_value(
                e, "event_timestamp") for e in preset]
            if len(end_timestamps) == 0:
                duration = 0
            else:
                ot_end_timestamps = [ocel.get_value(
                    e, "event_timestamp") for e in preset if ocel.get_value(e, ot)]
                duration = (max(end_timestamps) -
                            max(ot_end_timestamps)).total_seconds()
            readying_times.append(duration)
    return readying_times


def object_freq(ocel, act, ot):
    object_freqs = []
    for eid in ocel.obj.act_events[act]:
        object_freqs.append(len(ocel.obj.eve_ot_objects(eid, ot)))
    return object_freqs
