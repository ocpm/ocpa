ocpa.algo.filtering package
===========================

OCPA offers various filtering techniques for object-centric event logs, allowing to select subsets of the data based on activities, objects, time, attributes, lifecycle, performance, and variants.

Activity Filtering
__________________

Filters an Object-Centric Event Log to retain only events corresponding to specified activities, preserving related objects and event-object relationships while removing all unrelated data. In the following example, only events for 'Create Purchase Requisition', 'Receive Goods', and 'Issue Goods Receipt' are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import activity_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_using_list_of_activities = activity_filtering(
        ocel,
        ['Create Purchase Requisition', 'Receive Goods', 'Issue Goods Receipt']
    )

Activity Frequency Filtering
____________________________

Filters an Object-Centric Event Log by retaining only the most frequent activities until the specified cumulative frequency threshold is met. In the following example, activities are kept until they account for 80% of all events, and the rest are removed.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import activity_freq_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_using_activity_frequencies = activity_freq_filtering(ocel, 0.8)

Object Type Filtering
_____________________

Filters an Object-Centric Event Log by retaining only specified object types and all events related to them. In the following example, only objects of types 'PURCHORD' and 'INVOICE' and their associated events are kept; all other object types and unrelated events are removed.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import object_type_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_using_list_of_object_types = object_type_filtering(
        ocel,
        ['PURCHORD', 'INVOICE']
    )

Object Frequency Filtering
__________________________

Filters object types in an Object-Centric Event Log based on their frequency of participation in events, removing those whose involvement falls below a given threshold. In the example below, object types participating in less than 20% of events are filtered out.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import object_freq_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_using_object_type_frequencies = object_freq_filtering(ocel, 0.2)

Time-based Filtering
____________________

Filters cases in an Object-Centric Event Log based on specified time intervals using different strategies, such as filtering by case start time, end time, full containment within the interval, or cases spanning the interval. In the example, cases starting between May 4 and July 6, 2021, are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from datetime import datetime
    from ocpa.algo.util.filtering.log.index_based_filtering import time_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    start = datetime.fromisoformat('2021-05-04 09:02:00+01:00')
    end = datetime.fromisoformat('2021-07-06 09:00:00+01:00')

    filtered_based_on_time = time_filtering(
        ocel,
        start,
        end,
        strategy_name="start"  # Alternatives: "end", "contained", "spanning"
    )

Event Attribute Filtering
_________________________

Filters an Object-Centric Event Log by retaining only events that match specified attribute values. In the following example, only events with the activity 'Create Purchase Order' or 'Create Purchase Requisition' are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import event_attribute_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    attr_filter = {"event_activity": ["Create Purchase Order", "Create Purchase Requisition"]}
    filtered_based_on_event_attributes = event_attribute_filtering(ocel, attr_filter)

Object Attribute Filtering
__________________________

Filters an Object-Centric Event Log by retaining only events linked to objects that meet specified attribute cardinality conditions. In the example below, only events associated with more than two 'MATERIAL' objects and exactly one 'PURCHORD' object are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import object_attribute_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    vmap = {'MATERIAL': ['more than', 2], 'PURCHORD': ['exactly', 1]}
    filtered_based_on_object_attributes = object_attribute_filtering(ocel, vmap)

Object Lifecycle Filtering
__________________________

Filters an Object-Centric Event Log to retain only objects of a specified type that follow a given sequence of activities. In the following example, only 'PURCHORD' objects that go through 'Create Purchase Order', 'Receive Invoice', and 'Clear Invoice' in that order are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import object_lifecycle_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_using_control_flow_of_objects = object_lifecycle_filtering(
        ocel,
        object_type="PURCHORD",
        list_of_activities=["Create Purchase Order", "Receive Invoice", "Clear Invoice"]
    )

Event Performance-based Filtering
________________________________

Filters an Object-Centric Event Log based on performance measures (e.g., synchronization, flow, or sojourn time), retaining only events that meet a specified condition. In the following example, only 'Create Purchase Order' events with a synchronization time of less than 24 hours are kept.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import event_performance_based_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    parameters = {
        'measure': 'synchronization',
        'activity': 'Create Purchase Order',
        'condition': lambda x: x < 86400  # 24-hour threshold
    }
    filtered_using_event_performance = event_performance_based_filtering(ocel, parameters)

Variant Frequency Filtering
____________________________

Filters an Object-Centric Event Log by removing infrequent variants based on the given cumulative frequency threshold. In the following example, only the most common variants that together make up 80% of the total cases are retained.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import variant_frequency_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_ocel_variant_freq = variant_frequency_filtering(ocel, 0.8)

Variant Activity Sequence Filtering
___________________________________

Filters an Object-Centric Event Log to retain only process executions (variants) that contain specific activity transitions. In the following example, only executions that include the transition from 'Verify Material' to 'Plan Goods Issue' are kept.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.util.filtering.log.index_based_filtering import variant_activity_sequence_filtering

    filename = "sample_logs/jsonocel/exported-p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    filtered_ocel_with_act_to_act = variant_activity_sequence_filtering(
        ocel,
        [('Verify Material', 'Plan Goods Issue')]
    )

