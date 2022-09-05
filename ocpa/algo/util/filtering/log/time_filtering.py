from ocpa.algo.util.filtering.log import case_filtering
from ocpa.objects.log.util import misc as log_util

def start(start, end, exec_start, exec_end):
    '''
    Indicates whether a process execution belongs to a window given window start and end, and process execution start
    and end. A process execution belongs to a window if the start is located in the window.

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :param exec_start: Start of the process execution
    :type exec_start: timestamp

    :param exec_end: End of the process execution
    :type exec_end: timestamp

    :return: Whether the process execution belongs to the window
    :rtype: boolean

    '''
    return (exec_start >= start) & (exec_start <= end)


def spanning(start, end, exec_start, exec_end):
    '''
    Indicates whether a process execution belongs to a window given window start and end, and process execution start
    and end. A process execution belongs to a window if the there is an intersection between the window and the process
    execution time.

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :param exec_start: Start of the process execution
    :type exec_start: timestamp

    :param exec_end: End of the process execution
    :type exec_end: timestamp

    :return: Whether the process execution belongs to the window
    :rtype: boolean

    '''
    return ((exec_start <= start) & (exec_end >= start)) | ((exec_start <= end) & (exec_end >= end))


def end(start, end, exex_start, exec_end):
    '''
    Indicates whether a process execution belongs to a window given window start and end, and process execution start
    and end. A process execution belongs to a window if the end is located in the window.

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :param exec_start: Start of the process execution
    :type exec_start: timestamp

    :param exec_end: End of the process execution
    :type exec_end: timestamp

    :return: Whether the process execution belongs to the window
    :rtype: boolean

    '''
    return (exec_end >= start) & (exec_end <= end)


def contained(start, end, exec_start, exec_end):
    '''
    Indicates whether a process execution belongs to a window given window start and end, and process execution start
    and end. A process execution belongs to a window if the process execution is completely contained in the window.

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :param exec_start: Start of the process execution
    :type exec_start: timestamp

    :param exec_end: End of the process execution
    :type exec_end: timestamp

    :return: Whether the process execution belongs to the window
    :rtype: boolean

    '''
    return (exec_start >= start) & (exec_end <= end)


def extract_sublog(ocel, start, end, strategy):
    '''
    Returns the sub event log for a time window given the inclusion strategy.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :param strategy: function that takes an ocel, start and end of the window and start and end of a process execution and returns a boolean whether the process execution will be included. E.g., :func:`by start timestamp of the process execution <ocpa.algo.filtering.log.time_filtering.start>`:. Can also be :func:`by events <ocpa.algo.filtering.log.time_filtering.events>`:
    :type strategy: func

    :return: New sublog
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''


    if strategy == events:
        return events(ocel, start, end)
    cases = []
    mapping_time = dict(zip(ocel.log["event_id"], ocel.log["event_timestamp"]))
    #id_index = list(ocel.log.columns.values).index("event_id")
    #id_time = list(ocel.log.columns.values).index("event_timestamp")
    #arr = ocel.log.to_numpy()
    for i in range(0, len(ocel.process_executions)):
        case = ocel.process_executions[i]
        exec_start = min([mapping_time[e] for e in case])
        exec_end = max([mapping_time[e] for e in case])
        if strategy(start, end, exec_start, exec_end):
            cases += [ocel.process_executions[i]]

    return case_filtering.filter_process_executions(ocel, cases)


def events(ocel, start, end):
    '''
    Returns the sub event log for a time window.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param start: Start of the window
    :type start: timestamp

    :param end: End of the window
    :type end: timestamp

    :return: New sublog
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''
    events = []
    id_index = list(ocel.log.log.columns.values).index("event_id")
    id_time = list(ocel.log.log.columns.values).index("event_timestamp")
    arr = ocel.log.log.to_numpy()
    for line in arr:
        if (start <= line[id_time]) & (line[id_time] <= end):
            events.append(line[id_index])
    new_event_df = ocel.log.log[ocel.log.log['event_id'].isin(events)]
    new_ocel = log_util.copy_log_from_df(new_event_df,ocel.parameters)
    return new_ocel
