import networkx as nx

def apply(ocel,parameters):
    '''
    Extracting process executions through connected components of the object graph. Calling this method is usually
    integrated in the :class:`OCEL class <ocpa.objects.log.ocel.OCEL>` and is specified in the parameters usually set
    when importing the OCEL in :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    :return: cases, object_mapping, case_mapping

    '''
    case_mapping = {}
    log_df = ocel.log._log.copy()
    log_df["event_objects"] = log_df.apply(lambda x: set([(ot, o) for ot in ocel.object_types for o in x[ot]]),
                                       axis=1)
    cases = sorted(nx.weakly_connected_components(
        ocel.graph.eog), key=len, reverse=True)
    obs = []
    mapping_objects = dict(
        zip(log_df["event_id"], log_df["event_objects"]))
    for case in cases:
        case_obs = []
        for event in case:
            for ob in mapping_objects[event]:
                case_obs += [ob]
        obs.append(list(set(case_obs)))
    log_df.drop('event_objects', axis=1, inplace=True)
    for case_index in range(0, len(cases)):
        case = cases[case_index]
        for event in case:
            if not event in case_mapping.keys():
                case_mapping[event] = []
            case_mapping[event] += [case_index]
    return cases, obs, case_mapping