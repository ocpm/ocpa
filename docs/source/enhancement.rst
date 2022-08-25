Object-Centric Process Enhancement
############

Performance Analysis
_______________
OCPA offers object-centric performance analysis. The performance analysis considers the interaction of objects in business processes, producing accurate waiting, service, and sojourn times. Moreover, it provides insightful object-centric performance metrics such as lagging, pooling, synchronization, and flow times.

.. image:: _static/performance.png
   :width: 500px
   :align: center

New performance metrics on object-centric event data.

.. code-block:: python

    filename = "./sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    ocpn = ocpn_discovery_factory.apply(ocel)
    diag_params = {'measures': ['act_freq', 'arc_freq', 'object_count', 'waiting_time', 'service_time', 'sojourn_time', 'synchronization_time', 'pooling_time', 'lagging_time', 'flow_time'], 'agg': [
        'mean', 'min', 'max'], 'format': 'svg'}
    diag = performance_factory.apply(ocpn, ocel, parameters=diag_params)
    print(f'Diagnostics: {diag}')
    gviz = ocpn_vis_factory.apply(
        ocpn, diagnostics=diag, variant="annotated_with_opera", parameters=diag_params)
    ocpn_vis_factory.view(gviz)