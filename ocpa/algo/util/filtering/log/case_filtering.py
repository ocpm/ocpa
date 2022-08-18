from ocpa.objects.log.ocel import OCEL


def filter_process_executions(ocel, cases):
    '''
    Filters process executions from an ocel

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param cases: list of cases to be included (index of the case property of the OCEL)
    :type threshold: list(int)

    :return: Object-centric event log
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''

    events = [e for case in cases for e in case]
    new_event_df = ocel.log[ocel.log["event_id"].isin(events)].copy()
    new_log = OCEL(new_event_df, object_types=ocel.object_types, execution_extraction=ocel._execution_extraction,
                   leading_object_type=ocel._leading_type, variant_extraction=ocel._variant_extraction)
    return new_log
