Object-Centric Process Discovery
###############
A process model of the object-centric event log can be discovered by applying the discovery algorithm for object-centric Petri nets.
The corresponding retrieved object retrieved is of the class :class:`Object-centric Petri net <ocpa.objects.oc_petri_net.obj.ObjectCentricPetriNet>`.
Objects of this class can be visualized by calling the corresponding visualization function.

Object-Centric Petri Net Retrieval & Visualization
______________________________________

.. code-block:: python

    from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
    from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
    from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
    object_types = ["application", "offer"]
    parameters = {"obj_names":object_types,
                  "val_names":[],
                  "act_name":"event_activity",
                  "time_name":"event_timestamp",
                  "sep":",",}
    ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)
    ocpn = ocpn_discovery_factory.apply(ocel, parameters = {"debug":False})
    ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "oc_petri_net.svg")

Variant Calculation and Layouting
______________________________________
Equivalent control-flow behavior of process executions are called variants. Since a process execution is a graph, we can find equivalent process executions by annotating each graph's nodes with the activity attribute and finding isomorphic graphs.
OCPA offers two techniques to determine variants: By first calculating lexicographical presentations of the graphs and then refining these (TWO_PHASE), and through one-to-one isomorphism checking (ONE_PHASE). The first is normally faster. One can also choose to
use the approximation of variants through only the lexicographical presentation. This is the default procedure, but can be switched off by passing the right parameter (see example below).
The variant layouting just returns a positioning of chevrons as coordinates. The visualizaiton has to be done using another tool (www.ocpi.ai implements this end-to-end)

.. code-block:: python

    import ocpa
    from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
    from ocpa.visualization.log.variants import factory as variants_visualization_factory
    object_types = ["application", "offer"]
    parameters = {"obj_names":object_types,
                  "val_names":[],
                  "act_name":"event_activity",
                  "time_name":"event_timestamp",
                  "sep":",",
                  "execution_extraction":ocpa.algo.util.process_executions.factory.LEAD_TYPE,
                  "leading_type":object_types[0],
                  "variant_calculation":ocpa.algo.util.variants.factory.TWO_PHASE
                  "exact_variant_calculation":True}
    ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)
    print("Number of variants: "+str(len(ocel.variants)))
    variant_layouting = variants_visualization_factory.apply(ocel)
