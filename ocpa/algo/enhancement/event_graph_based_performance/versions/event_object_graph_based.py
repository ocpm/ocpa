from ocpa.util.util import AGG_MAP



def apply(ocel, parameters):
    """
    Apply performance measure and aggregation function on the given ocel object and parameters.

    :param ocel: ocel object
    :param parameters: dict with keys 'measure', 'activity', 'object_type', and 'aggregation'
    :return: aggregated performance measure
    """
    measure = parameters.get('measure')
    if not measure:
        raise ValueError('Specify a performance measure in parameters')

    act = parameters.get('activity')
    if not act:
        raise ValueError('Specify an activity in parameters')

    ot = parameters.get('object_type')

    agg = parameters.get('aggregation')
    if not agg:
        raise ValueError('Specify an aggregation function in parameters')

    measure_function_mapping = {
        'flow': flow_time,
        'sojourn': sojourn_time,
        'synchronization': synchronization_time,
        'pooling': pooling_time,
        'lagging': lagging_time,
        'rediness': readiness_time,
        'elapsed': elapsed_time,
        'remaining': remaining_time,
        'object_freq': object_freq,
        'act_freq': act_freq
    }

    function = measure_function_mapping.get(measure)
    if not function:
        raise ValueError(f"Unknown performance measure: {measure}")

    if measure in {'pooling', 'lagging', 'rediness', 'object_freq', 'elapsed', 'remaining'} and ot is None:
        raise ValueError('Specify an object type in parameters')
    measurements = function(ocel, act, ot)
    if len(measurements) > 0:
        return AGG_MAP[agg](measurements)
    else:
        return 0


def flow_time(ocel, act, ot=None):
    """
    Calculate flow times for a given activity in the ocel object.

    :param ocel: ocel object
    :param act: activity name
    :return: list of flow times
    """
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


def sojourn_time(ocel, act, ot=None):
    """
    Calculate sojourn times for a given activity in the ocel object.

    :param ocel: ocel object
    :param act: activity name
    :return: list of sojourn times
    """
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


def synchronization_time(ocel, act, ot=None):
    """
    Calculate synchronization times for a given activity in the ocel object.
     :param ocel: ocel object
    :param act: activity name
    :return: list of synchronization times
    """
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


def pooling_time(ocel, act, ot):
    """
    Calculate pooling times for a given activity and object type in the ocel object.

    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of pooling times
    """
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
    """
    Calculate lagging times for a given activity and object type in the ocel object.

    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of lagging times
    """
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


def readiness_time(ocel, act, ot):
    """
    Calculate rediness times for a given activity and object type in the ocel object.

    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of rediness times
    """
    readiness_times = []
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
            duration = (min(ot_end_timestamps) - min(end_timestamps)).total_seconds()
        readiness_times.append(duration)
    return readiness_times

def object_freq(ocel, act, ot):
    """
    Calculate object frequencies for a given activity and object type in the ocel object.
    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of object frequencies
    """
    obj_freqs = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            obj_freq = len(ocel.get_value(node, ot))
            obj_freqs.append(obj_freq)
    return obj_freqs

def act_freq(ocel, act, ot):
    """
    Calculate object frequencies for a given activity and object type in the ocel object.
    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of object frequencies
    """
    act_freqs = []
    for o in ocel.obj.ot_objects[ot]:
        act_freq = len([e for e in ocel.obj.sequence[o] if e.act == act])
        act_freqs.append(act_freq)
    return act_freqs

def elapsed_time(ocel, act, ot):
    """
    Calculate elapsed times for a given activity and object type in the ocel object.
    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of elapsed times
    """
    elapsed_time = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            in_edges = ocel.graph.eog.in_edges(node)
            preset = [source for (source, target) in in_edges]
            if len(preset) == 0:
                duration = 0
            else:
                duration = (ocel.get_value(node, "event_timestamp") - max([ocel.get_value(
                    e, "event_timestamp") for e in preset])).total_seconds()
            elapsed_time.append(duration)
    return elapsed_time

def remaining_time(ocel, act, ot):
    """
    Calculate remaining times for a given activity and object type in the ocel object.
    :param ocel: ocel object
    :param act: activity name
    :param ot: object type
    :return: list of remaining times
    """
    remaining_times = []
    for node in ocel.graph.eog.nodes:
        if ocel.get_value(node, "event_activity") == act:
            out_edges = ocel.graph.eog.out_edges(node)
            postset = [target for (source, target) in out_edges]
            if len(postset) == 0:
                duration = 0
            else:
                duration = (max([ocel.get_value(
                    e, "event_timestamp") for e in postset]) - ocel.get_value(node, "event_timestamp")).total_seconds()
            remaining_times.append(duration)
    return remaining_times
