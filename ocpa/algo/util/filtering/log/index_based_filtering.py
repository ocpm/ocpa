from collections import Counter
import networkx as nx
import pandas as pd
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
from ocpa.objects.log.variants.obj import MetaObjectCentricData, RawObjectCentricData, ObjectCentricEventLog


def activity_filtering(ocel, activity_list):
    '''
    Filters an OCEL (Object-Centric Event Log) to retain only specified activities.

    This function keeps only the events corresponding to the given list of activity names
    in the OCEL log. It updates the event graph by preserving only the relevant nodes and edges,
    and filters the object-related data accordingly to maintain consistency.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param activity_list: List of activity names to retain in the log.
    :type activity_list: list[str]

    :return: A new OCEL object with only specified activities removed from log, graph, and object mapping.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Extract event IDs associated with activities to be removed and filter the event log DataFrame
    removed_event_ids = ocel.log.log[~ocel.log.log["event_activity"].isin(activity_list)]["event_id"].tolist()
    filtered_df = ocel.log.log[ocel.log.log["event_activity"].isin(activity_list)].copy()
    filtered_log = Table(filtered_df, ocel.parameters)

    # Step 2: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 3: Filter the object-centric structure by updating raw events, objects, and object-event mappings
    new_events = ocel.obj.raw.events.copy()
    new_objects = ocel.obj.raw.objects.copy()
    new_obj_event_mapping = {}
    for eid in removed_event_ids:
        new_events.pop(eid, None)

    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]
        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    raw_new = RawObjectCentricData(
        events=new_events,
        objects=new_objects,
        obj_event_mapping=new_obj_event_mapping
    )
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Step 4: Construct and return a new OCEL object using the filtered log, graph, and object data
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


def activity_freq_filtering(ocel, threshold):
    '''
    Filters out infrequent activities from an OCEL based on a cumulative frequency threshold.

    Activities are ranked by frequency, and the most frequent activities are retained until their
    cumulative frequency exceeds the threshold. All remaining activities are considered infrequent
    and are removed from the log.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param threshold: Cumulative frequency threshold (between 0 and 1) used to retain the most frequent activities.
    :type threshold: float

    :return: A new OCEL object with infrequent activities removed.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Compute activity frequency distribution
    activity_distribution = Counter(ocel.log.log["event_activity"].values.tolist())

    # Step 2: Normalize frequencies to get relative activity frequencies
    activities, frequencies = map(
        list,
        zip(*[(a, f / len(list(activity_distribution.elements())))
              for (a, f) in activity_distribution.most_common()])
    )

    # Step 3: Compute cumulative frequency and find the cutoff point
    freq_acc = [sum(frequencies[0:i + 1]) for i in range(0, len(frequencies))]
    last_filtered_activity = len(freq_acc) - 1
    for i in range(0, len(freq_acc)):
        if freq_acc[i] > threshold:
            last_filtered_activity = i
            break

    # Step 4: Identify frequent vs. infrequent activities based on cutoff
    filtered_activities = activities[:last_filtered_activity + 1]
    
    # Step 5: Use activity_filtering() to remove the infrequent activities
    filtered_ocel = activity_filtering(ocel, filtered_activities)
    return filtered_ocel


def object_type_filtering(ocel, object_type_list):
    '''
    Filters specified object types from an OCEL (Object-Centric Event Log).

    This function removes all objects of the given types from the log,
    along with their related events. It updates the event graph and
    the object structure to maintain consistency.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param object_type_list: List of object types to be removed from the OCEL.
    :type object_type_list: list[str]

    :return: A new OCEL object with specified object types removed.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Create a mask to keep only those events that do NOT reference the object types being removed
    mask = ocel.log.log.apply(
        lambda row: all(
            (isinstance(row[col], list) and len(row[col]) == 0)
            for col in object_type_list
        ), axis=1)

    # Step 2: Filter the event log using the mask and collect the event IDs that are being removed
    filtered_df = ocel.log.log[mask]
    filtered_log = Table(filtered_df, ocel.parameters)
    removed_eventIDs = ocel.log.log[~mask]['event_id'].tolist()

    # Step 3: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_eventIDs)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_eventIDs) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 4: Remove events and objects of the specified types from the object model
    filtered_events = {k: v for k, v in ocel.obj.raw.events.items() if k not in removed_eventIDs}
    keys_to_remove = {key for key, obj in ocel.obj.raw.objects.items() if obj.type in object_type_list}
    filtered_objects = {key: obj for key, obj in ocel.obj.raw.objects.items() if key not in keys_to_remove}

    # Step 5: Update object-event mapping to reflect the removal of objects and events
    filtered_event_mapping = {
        key: [eid for eid in val if eid not in removed_eventIDs]
        for key, val in ocel.obj.raw.obj_event_mapping.items()
        if key in filtered_objects
    }

    # Step 6: Update the object-centric metadata (remove the object types from the meta info)
    filtered_obj_types = [obj_type for obj_type in ocel.obj.meta.obj_types if obj_type not in object_type_list]
    meta_new = MetaObjectCentricData(
        attr_names=ocel.obj.meta.attr_names,
        attr_types=ocel.obj.meta.attr_types,
        attr_typ=ocel.obj.meta.attr_typ,
        obj_types=filtered_obj_types,
        act_attr=ocel.obj.meta.act_attr,
        attr_events=ocel.obj.meta.attr_events
    )

    # Step 7: Build the new OCEL object and return it
    raw_new = RawObjectCentricData(
        events=filtered_events,
        objects=filtered_objects,
        obj_event_mapping=filtered_event_mapping
    )
    obj_new = ObjectCentricEventLog(meta=meta_new, raw=raw_new)

    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


def object_freq_filtering(ocel, threshold):
    '''
    Filters object types from an OCEL based on their relative frequency.

    This function calculates the frequency of each object type across the event log.
    It then removes the object types whose relative frequency (compared to the total object participation)
    falls below the given threshold.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param threshold: Minimum relative frequency required to retain an object type.
    :type threshold: float (between 0 and 1)

    :return: A new OCEL object with low-frequency object types removed.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Get all object types in the log
    all_object_types = ocel.obj.meta.obj_types

    # Step 2: Compute frequency (number of associations) of each object type across all events
    frequencies = {}
    for ot in all_object_types:
        frequencies[ot] = ocel.log.log[ot].apply(len).sum()

    # Step 3: Compute relative frequency for each object type
    freq_acc = {k: v / sum(frequencies.values()) for k, v in frequencies.items()}

    # Step 4: Identify object types whose relative frequency is below the threshold
    object_types_to_remove = [k for k, v in freq_acc.items() if v < threshold]

    # Step 5: Use object_type_filtering to remove the low-frequency object types
    filtered_ocel = object_type_filtering(ocel, object_types_to_remove)

    return filtered_ocel


def time_filtering(ocel, start_time, end_time, strategy_name="start"):
    '''
    Filters the OCEL based on the selected time-based strategy.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param start_time: Start of the time window
    :type start_time: timestamp

    :param end_time: End of the time window
    :type end_time: timestamp

    :param strategy_name: The filtering strategy to use, one of ["start", "spanning", "end", "contained", "events"]
    :type strategy_name: str

    :return: New OCEL after applying the time-based filtering
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Strategy definitions for filtering execution intervals
    def start(start_time, end_time, exec_start, exec_end):
        return (exec_start >= start_time) & (exec_start <= end_time)

    def spanning(start_time, end_time, exec_start, exec_end):
        return ((exec_start <= start_time) & (exec_end >= start_time)) | (
                (exec_start <= end_time) & (exec_end >= end_time))

    def end(start_time, end_time, exec_start, exec_end):
        return (exec_end >= start_time) & (exec_end <= end_time)

    def contained(start_time, end_time, exec_start, exec_end):
        return (exec_start >= start_time) & (exec_end <= end_time)

    # Event-level strategy: filter individual events by timestamp
    def events(ocel, start_time=None, end_time=None):
        events = []
        id_index = list(ocel.log.log.columns.values).index("event_id")
        id_time = list(ocel.log.log.columns.values).index("event_timestamp")
        arr = ocel.log.log.to_numpy()

        for line in arr:
            if start_time is not None and end_time is None:
                if start_time <= line[id_time]:
                    events.append(line[id_index])
            elif start_time is None and end_time is not None:
                if line[id_time] <= end_time:
                    events.append(line[id_index])
            elif start_time is not None and end_time is not None:
                if (start_time <= line[id_time]) & (line[id_time] <= end_time):
                    events.append(line[id_index])
            else:
                raise ValueError('Specify either start_time or end_time timestamp')

        # Get IDs of events to be removed
        all_event_ids = ocel.log.log["event_id"].tolist()
        removed_event_ids = list(set(all_event_ids) - set(events))

        # Filter the dataframe to include only selected events
        filtered_df = ocel.log.log[ocel.log.log['event_id'].isin(events)]
        filtered_log = Table(filtered_df, ocel.parameters)

        # Create a new graph with only the nodes and edges we want to keep
        G = nx.DiGraph()
        # Add only the nodes we want to keep
        nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
        G.add_nodes_from(nodes_to_keep)
        # Add only the edges that don't involve removed nodes
        edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
        G.add_edges_from(edges_to_keep)
        filtered_graph = EventGraph(G)

        # Filter raw event-object data
        new_events = ocel.obj.raw.events.copy()
        new_objects = ocel.obj.raw.objects.copy()
        new_obj_event_mapping = {}

        for eid in removed_event_ids:
            new_events.pop(eid, None)
        removed_objects = set()
        for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
            filtered_events = [eid for eid in event_list if eid not in removed_event_ids]
            if filtered_events:
                new_obj_event_mapping[obj_id] = filtered_events
            else:
                removed_objects.add(obj_id)
        for obj_id in removed_objects:
            new_objects.pop(obj_id, None)

        # Create new object structure
        raw_new = RawObjectCentricData(events=new_events, objects=new_objects,
                                       obj_event_mapping=new_obj_event_mapping)
        obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

        # Construct new OCEL
        filtered_ocel = OCEL(
            log=filtered_log,
            graph=filtered_graph,
            parameters=ocel.parameters,
            obj=obj_new,
        )
        return filtered_ocel

    # Map strategy names to corresponding filtering functions
    strategy_map = {
        "start": start,
        "spanning": spanning,
        "end": end,
        "contained": contained,
        "events": events
    }

    # Validate strategy name
    if strategy_name not in strategy_map:
        raise ValueError(f"Invalid strategy_name. Choose from {list(strategy_map.keys())}")

    # Apply "events" strategy separately since it's handled differently
    strategy = strategy_map[strategy_name]
    if strategy_name == "events":
        return strategy(ocel, start_time, end_time)

    # Otherwise apply case-level strategy
    cases = []
    removed_event_ids = []
    mapping_time = dict(zip(ocel.log.log["event_id"], ocel.log.log["event_timestamp"]))

    # Identify cases to remove based on strategy
    for case in ocel.process_executions:
        exec_start = min([mapping_time[e] for e in case])
        exec_end = max([mapping_time[e] for e in case])
        if not strategy(start_time, end_time, exec_start, exec_end):
            cases.append(case)
            for e in case:
                removed_event_ids.append(e)

    # Filter raw event-object data
    new_events = ocel.obj.raw.events.copy()
    new_objects = ocel.obj.raw.objects.copy()
    new_obj_event_mapping = {}

    for eid in removed_event_ids:
        new_events.pop(eid, None)
    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]
        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    raw_new = RawObjectCentricData(events=new_events, objects=new_objects,
                                   obj_event_mapping=new_obj_event_mapping)
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Filter the dataframe
    filtered_df = ocel.log.log.iloc[[i for i in range(len(ocel.log.log)) if i not in removed_event_ids]]
    filtered_log = Table(filtered_df, ocel.parameters)

    # Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Return final filtered OCEL
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


def event_attribute_filtering(ocel, attr_filter):
    '''
    Filters events from an OCEL based on specified event attribute conditions.

    This function removes events that do not satisfy the given attribute filter from the log.
    It updates the event graph and the object-centric structure accordingly to maintain consistency.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param attr_filter: Dictionary where keys are event attribute names and values are the values or list of values to filter for.
    :type attr_filter: dict[str, Union[str, list[str]]]

    :return: A new OCEL object with events filtered based on attribute conditions.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Filter the DataFrame based on the given attribute filter conditions
    df = ocel.log.log.copy()
    condition = pd.Series([True] * len(df), index=df.index)

    for key, value in attr_filter.items():
        if isinstance(value, list):
            condition &= df[key].isin(value)
        else:
            condition &= df[key] == value

    df_filtered = df[condition]
    removed_event_ids = list(df.index.difference(df_filtered.index))
    filtered_log = Table(df_filtered, ocel.parameters)

    # Step 2: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 3: Update the object-centric structure (events, objects, and object-event mapping)
    new_events = ocel.obj.raw.events.copy()
    new_objects = ocel.obj.raw.objects.copy()
    new_obj_event_mapping = {}
    for eid in removed_event_ids:
        new_events.pop(eid, None)

    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]

        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    raw_new = RawObjectCentricData(
        events=new_events,
        objects=new_objects,
        obj_event_mapping=new_obj_event_mapping
    )
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Step 4: Create and return the new OCEL object
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


# filtering objects based on their lifecycle (control-flow)
def object_lifecycle_filtering(ocel, object_type, list_of_activities):
    '''
    Filters events based on whether objects of a given type exhibit a specific sequence of activities.

    Only those objects whose lifecycle (i.e., sequence of activities over time)
    includes the specified list of activities as a subsequence are retained.
    All events related to other objects are removed, and the OCEL is filtered accordingly.

    :param ocel: The object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param object_type: The prefix identifying the object type to check for the activity subsequence.
    :type object_type: str

    :param list_of_activities: Ordered list of activities that must appear (as a subsequence) in the object's lifecycle.
    :type list_of_activities: list[str]

    :return: A filtered OCEL containing only the events of objects that match the specified activity subsequence.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Extract the full event log and object-event mapping
    df = ocel.log.log
    obj_event_mapping = ocel.obj.raw.obj_event_mapping

    # Step 2: Select only objects of the specified type
    selected_objects = [
        obj for obj in obj_event_mapping.keys()
        if obj.startswith(object_type)
    ]

    # Step 3: Find objects whose activity sequence contains the specified subsequence
    matching_event_ids = set()
    for obj in selected_objects:
        event_ids = obj_event_mapping[obj]
        events = df.loc[event_ids].sort_values("event_timestamp")
        activity_sequence = events["event_activity"].tolist()

        # Check for presence of the activity subsequence
        current_pos = 0
        match = True
        for activity in list_of_activities:
            try:
                current_pos = activity_sequence.index(activity, current_pos) + 1
            except ValueError:
                match = False
                break
        if match:
            matching_event_ids.update(event_ids)

    # Step 4: Filter the log to only include matching event IDs
    filtered_df = df.loc[list(matching_event_ids)]
    original_event_ids = set(df['event_id'].tolist())
    filtered_event_ids = set(filtered_df['event_id'].tolist())
    removed_event_ids = list(original_event_ids - filtered_event_ids)
    filtered_log = Table(filtered_df, ocel.parameters)

    # Step 5: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 6: Filter the object structure (events, objects, and object-event mapping)
    new_events = ocel.obj.raw.events.copy()
    new_objects = ocel.obj.raw.objects.copy()
    new_obj_event_mapping = {}
    for eid in removed_event_ids:
        new_events.pop(eid, None)

    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]
        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    raw_new = RawObjectCentricData(
        events=new_events,
        objects=new_objects,
        obj_event_mapping=new_obj_event_mapping
    )
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Step 7: Reconstruct and return the filtered OCEL object
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


def object_attribute_filtering(ocel, vmap):
    '''
    Filters events in an OCEL based on object attribute conditions.

    This function applies a series of conditions on object attribute columns in the OCEL log
    and filters events that meet the given criteria. The event graph and object-related data
    are also updated accordingly to ensure consistency.

    :param ocel: Object-centric event log to be filtered.
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param vmap: Dictionary containing the filtering conditions for each column in the log.
    :type vmap: dict

    :return: A new OCEL object with filtered events, graph, and object mappings.
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    '''

    # Step 1: Initialize a mask for filtering based on the conditions in vmap
    df = ocel.log.log.copy()
    mask = pd.Series(True, index=df.index)

    # Step 2: Apply conditions from vmap to each column
    for column, (condition, number) in vmap.items():
        # Calculate the length of each list in the column
        lengths = df[column].apply(len)

        # Determine the condition for filtering
        if condition == 'less than':
            col_mask = lengths < number
        elif condition == 'exactly':
            col_mask = lengths == number
        elif condition == 'more than':
            col_mask = lengths > number
        else:
            raise ValueError(
                f"Invalid condition '{condition}' for column '{column}'. Use 'less than', 'exactly', or 'more than'.")

        # Update the overall mask with the current column's mask
        mask = mask & col_mask

    # Step 3: Apply the mask to filter the dataframe
    filtered_df = df[mask]

    # Step 4: Identify and remove events based on the filter mask
    removed_event_ids = df.index[~mask].tolist()
    filtered_log = Table(filtered_df, ocel.parameters)

    # Step 5: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 6: Update object-centric data (events, objects, and mappings)
    new_events = ocel.obj.raw.events.copy()  # Shallow copy of events dict
    new_objects = ocel.obj.raw.objects.copy()  # Shallow copy of objects dict
    new_obj_event_mapping = {}  # Will build this from scratch
    for eid in removed_event_ids:
        new_events.pop(eid, None)

    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]

        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    # Step 7: Construct and return a new OCEL object using the filtered log, graph, and object data
    raw_new = RawObjectCentricData(
        events=new_events,
        objects=new_objects,
        obj_event_mapping=new_obj_event_mapping
    )
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Step 8: Return the filtered OCEL object
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel


def event_performance_based_filtering(ocel, parameters):
    """
    Filters events based on a performance measure and a condition.

    :param ocel: Object-Centric Event Log
    :param parameters: Dictionary containing 'measure', 'activity', 'object_type' (if required), and 'condition'
    :return: Filtered DataFrame of the event log
    """

    # Step 1: Validate parameters
    measure = parameters.get('measure')
    if not measure:
        raise ValueError('Specify a performance measure in parameters')

    activity = parameters.get('activity')
    if not activity:
        raise ValueError('Specify an activity in parameters')

    object_type = parameters.get('object_type')
    condition = parameters.get('condition')

    # Check if the condition is a callable function
    if not callable(condition):
        raise ValueError('Condition must be a callable function')

    # Step 2: Check if the measure requires an object_type
    measures_requiring_ot = {'pooling', 'lagging', 'rediness', 'object_freq'}
    if measure in measures_requiring_ot and not object_type:
        raise ValueError(f"Measure '{measure}' requires an object_type parameter")

    # Step 3: Get all events of the specified activity from the log DataFrame
    log_df = ocel.log.log
    activity_events = log_df[log_df['event_activity'] == activity].index.tolist()

    # Step 4: Define helper functions to compute each performance measure for a single event
    def compute_flow_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        timestamps = [ocel.get_value(pred, "event_timestamp") for pred in predecessors]
        if not timestamps:
            return 0.0
        current_time = ocel.get_value(event_id, "event_timestamp")
        return (current_time - min(timestamps)).total_seconds()

    def compute_sojourn_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        timestamps = [ocel.get_value(pred, "event_timestamp") for pred in predecessors]
        if not timestamps:
            return 0.0
        current_time = ocel.get_value(event_id, "event_timestamp")
        return (current_time - max(timestamps)).total_seconds()

    def compute_synchronization_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        timestamps = [ocel.get_value(pred, "event_timestamp") for pred in predecessors]
        if len(timestamps) < 2:
            return 0.0
        return (max(timestamps) - min(timestamps)).total_seconds()

    def compute_pooling_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        ot_predecessors = [pred for pred in predecessors if ocel.get_value(pred, object_type)]
        timestamps = [ocel.get_value(pred, "event_timestamp") for pred in ot_predecessors]
        if len(timestamps) < 2:
            return 0.0
        return (max(timestamps) - min(timestamps)).total_seconds()

    def compute_lagging_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        all_timestamps = [ocel.get_value(pred, "event_timestamp") for pred in predecessors]
        if not all_timestamps:
            return 0.0
        ot_predecessors = [pred for pred in predecessors if ocel.get_value(pred, object_type)]
        if not ot_predecessors:
            return 0.0
        ot_timestamps = [ocel.get_value(pred, "event_timestamp") for pred in ot_predecessors]
        return (max(ot_timestamps) - min(all_timestamps)).total_seconds()

    def compute_rediness_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        all_timestamps = [ocel.get_value(pred, "event_timestamp") for pred in predecessors]
        if not all_timestamps:
            return 0.0
        ot_predecessors = [pred for pred in predecessors if ocel.get_value(pred, object_type)]
        if not ot_predecessors:
            return 0.0
        ot_timestamps = [ocel.get_value(pred, "event_timestamp") for pred in ot_predecessors]
        return (min(ot_timestamps) - min(all_timestamps)).total_seconds()

    def compute_elapsed_time(event_id):
        predecessors = list(ocel.graph.eog.predecessors(event_id))
        if not predecessors:
            return 0.0
        max_pred_ts = max(ocel.get_value(pred, "event_timestamp") for pred in predecessors)
        current_ts = ocel.get_value(event_id, "event_timestamp")
        return (current_ts - max_pred_ts).total_seconds()

    def compute_remaining_time(event_id):
        successors = list(ocel.graph.eog.successors(event_id))
        if not successors:
            return 0.0
        max_succ_ts = max(ocel.get_value(succ, "event_timestamp") for succ in successors)
        current_ts = ocel.get_value(event_id, "event_timestamp")
        return (max_succ_ts - current_ts).total_seconds()

    def compute_object_freq(event_id):
        return len(ocel.get_value(event_id, object_type))

    # Step 5: Mapping of measure to compute function
    measure_function_mapping = {
        'flow': compute_flow_time,
        'sojourn': compute_sojourn_time,
        'synchronization': compute_synchronization_time,
        'pooling': compute_pooling_time,
        'lagging': compute_lagging_time,
        'rediness': compute_rediness_time,
        'elapsed': compute_elapsed_time,
        'remaining': compute_remaining_time,
        'object_freq': compute_object_freq
    }

    # Step 6: Ensure the measure is supported
    if measure not in measure_function_mapping:
        raise ValueError(f"Unsupported performance measure: {measure}")

    compute_function = measure_function_mapping[measure]

    # Step 7: Evaluate each event and apply the condition
    filtered_event_ids = []
    for event_id in activity_events:
        try:
            value = compute_function(event_id)
        except KeyError as e:
            raise ValueError(f"Error computing measure {measure} for event {event_id}: {str(e)}")
        if condition(value):
            filtered_event_ids.append(event_id)

    # Step 8: Create a filtered DataFrame and calculate removed event IDs
    original_event_ids = set(log_df['event_id'].tolist())
    filtered_df = log_df.loc[filtered_event_ids]
    removed_event_ids = list(original_event_ids - set(filtered_event_ids))
    filtered_log = Table(filtered_df, ocel.parameters)
    
    # Step 9: Create a new graph with only the nodes and edges we want to keep
    G = nx.DiGraph()
    # Add only the nodes we want to keep
    nodes_to_keep = set(ocel.graph.eog.nodes) - set(removed_event_ids)
    G.add_nodes_from(nodes_to_keep)
    # Add only the edges that don't involve removed nodes
    edges_to_keep = {tup for tup in set(ocel.graph.eog.edges) if not any(x in set(removed_event_ids) for x in tup)}
    G.add_edges_from(edges_to_keep)
    filtered_graph = EventGraph(G)

    # Step 10: Filter the object-centric data structure (events, objects, obj_event_mapping)
    new_events = ocel.obj.raw.events.copy()  # Shallow copy of events dict
    new_objects = ocel.obj.raw.objects.copy()  # Shallow copy of objects dict
    new_obj_event_mapping = {}  # Will rebuild this mapping from scratch
    for eid in removed_event_ids:
        new_events.pop(eid, None)
    removed_objects = set()
    for obj_id, event_list in ocel.obj.raw.obj_event_mapping.items():
        filtered_events = [eid for eid in event_list if eid not in removed_event_ids]
        if filtered_events:
            new_obj_event_mapping[obj_id] = filtered_events
        else:
            removed_objects.add(obj_id)
    for obj_id in removed_objects:
        new_objects.pop(obj_id, None)

    # Step 11: Create a new RawObjectCentricData object with the filtered data
    raw_new = RawObjectCentricData(events=new_events, objects=new_objects,
                                   obj_event_mapping=new_obj_event_mapping)
    obj_new = ObjectCentricEventLog(meta=ocel.obj.meta, raw=raw_new)

    # Step 12: Return the filtered OCEL object
    filtered_ocel = OCEL(
        log=filtered_log,
        graph=filtered_graph,
        parameters=ocel.parameters,
        obj=obj_new,
    )
    return filtered_ocel
