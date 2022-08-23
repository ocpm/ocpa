import itertools
import networkx as nx
def apply(ocel, parameters):
    '''
    Extracting process executions through leading type extraction of the object graph. Calling this method is usually
    integrated in the :class:`OCEL class <ocpa.objects.log.ocel.OCEL>` and is specified in the parameters usually set
    when importing the OCEL in :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    :param parameters: Dictionary containing leading_type (usually already set when importing the event log)
    :type parameters: Dict
    :return: cases, object_mapping, case_mapping

    '''
    case_mapping = {}
    log_df = ocel.log.log.copy()
    log_df["event_objects"] = log_df.apply(lambda x: set([(ot, o) for ot in ocel.object_types for o in x[ot]]),
                                       axis=1)
    OG = nx.Graph()
    OG.add_nodes_from(log_df["event_objects"].explode(
        "event_objects").to_list())
    # ot_index = {ot: list(ocel.values).index(ot) for ot in self.object_types}
    object_index = list(log_df.columns.values).index("event_objects")
    id_index = list(log_df.columns.values).index("event_id")
    edge_list = []
    cases = []
    obs = []
    # build object graph
    arr = log_df.to_numpy()
    for i in range(0, len(arr)):
        edge_list += list(itertools.combinations(
            arr[i][object_index], 2))
    edge_list = [x for x in edge_list if x]
    OG.add_edges_from(edge_list)
    # construct a mapping for each object
    object_event_mapping = {}
    for i in range(0, len(arr)):
        for ob in arr[i][object_index]:
            if ob not in object_event_mapping.keys():
                object_event_mapping[ob] = []
            object_event_mapping[ob].append(arr[i][id_index])

    # for each leading object extract the case
    leading_type = parameters["leading_type"]
    for node in OG.nodes:
        case = []
        if node[0] != leading_type:
            continue
        relevant_objects = []
        ot_mapping = {}
        o_mapping = {}
        ot_mapping[leading_type] = 0
        next_level_objects = OG.neighbors(node)
        # relevant_objects += next_level_objects
        for level in range(1, len(ocel.object_types)):
            to_be_next_level = []
            for (ot, o) in next_level_objects:
                if ot not in ot_mapping.keys():
                    ot_mapping[ot] = level
                else:
                    if ot_mapping[ot] != level:
                        continue
                relevant_objects.append((ot, o))
                o_mapping[(ot, o)] = level
                to_be_next_level += OG.neighbors((ot, o))
            next_level_objects = to_be_next_level

        relevant_objects = set(relevant_objects)
        # add all leading events, and all events where only relevant objects are included
        obs_case = relevant_objects.union(set([node]))
        events_to_add = []
        for ob in obs_case:
            events_to_add += object_event_mapping[ob]
        events_to_add = list(set(events_to_add))
        case = events_to_add
        cases.append(case)
        obs.append(list(obs_case))
    log_df.drop('event_objects', axis=1, inplace=True)
    # create case mapping
    case_mapping = {}
    for case_index in range(0, len(cases)):
        case = cases[case_index]
        for event in case:
            if not event in case_mapping.keys():
                case_mapping[event] = []
            case_mapping[event] += [case_index]
    return cases, obs, case_mapping