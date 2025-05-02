# Test functions
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.filtering.log.index_based_filtering import activity_filtering, activity_freq_filtering, object_type_filtering, object_freq_filtering, time_filtering, event_attribute_filtering, object_attribute_filtering, object_lifecycle_filtering, event_performance_based_filtering

filename = "../../sample_logs/jsonocel/exported-p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)

# 1. Filter by explicitly removing specific activities from the log
# Removes all events related to 'Create Purchase Requisition', 'Receive Goods', and 'Issue Goods Receipt'
filtered_using_list_of_activities = activity_filtering(
    ocel,
    ['Create Purchase Requisition', 'Receive Goods', 'Issue Goods Receipt']
)

# 2. Filter activities by frequency - keep most frequent activities until cumulative 20% threshold
# Retains activities that together account for ≥20% of total activity occurrences
filtered_using_activity_frequencies = activity_freq_filtering(ocel, 0.2)

# 3. Filter by removing specific object types and their related events
# Removes all PURCHORD and INVOICE objects and their associated events
filtered_using_list_of_object_types = object_type_filtering(
    ocel,
    ['PURCHORD', 'INVOICE']
)

# 4. Filter object types by participation frequency - remove types with <20% relative frequency
# Eliminates object types that participate in less than 20% of total object-event relationships
filtered_using_object_type_frequencies = object_freq_filtering(ocel, 0.2)

# 5. Temporal filtering using "start" strategy between 2021-05-04 and 2021-07-06
# Keeps cases where the first event in the case occurs within specified timeframe
from datetime import datetime
start_str = '2021-05-04 09:02:00+01:00'
start = datetime.fromisoformat(start_str)
end_str = '2021-07-06 09:00:00+01:00'
end = datetime.fromisoformat(end_str)
filtered_based_on_time = time_filtering(
    ocel,
    start,
    end,
    strategy_name="start"  # Alternatives: "end", "contained", "spanning"
)

# 6. Filter events based on specific attribute values
# Retains only events with activity = "Create Purchase Order" or "Create Purchase Requisition"
attr_filter = {"event_activity": ["Create Purchase Order", "Create Purchase Requisition"]}
filtered_based_on_event_attributes = event_attribute_filtering(ocel, attr_filter)

# 7. Filter events based on object attribute cardinality
# - Keep events with >2 MATERIAL objects associated
# - Keep events with exactly 1 PURCHORD object associated
vmap = {'MATERIAL': ['more than', 2], 'PURCHORD': ['exactly', 1]}
filtered_based_on_object_attributes = object_attribute_filtering(ocel, vmap)

# 8. Filter based on object lifecycle patterns
# Retain only PURCHORD objects that go through specified activity sequence:
# "Create Purchase Order" → "Receive Invoice" → "Clear Invoice" (in order)
filtered_using_control_flow_of_objects = object_lifecycle_filtering(
    ocel,
    object_type="PURCHORD",
    list_of_activities=["Create Purchase Order", "Receive Invoice", "Clear Invoice"]
)

# 9. Performance-based filtering using synchronization time
# Keep "Create Purchase Order" events where synchronization time < 24 hours (86400 seconds)
# Synchronization time = time difference between first and last predecessor event
parameters = {
    'measure': 'synchronization',
    'activity': 'Create Purchase Order',
    'condition': lambda x: x < 86400  # 24-hour threshold
}
filtered_using_event_performance = event_performance_based_filtering(ocel, parameters)