Object-Centric Process Discovery
###############
A process model of the object-centric event log can be discovered by applying the discovery algorithm for object-centric Petri nets.
The corresponding retrieved object retrieved is of the class :class:`Object-centric Petri net <ocpa.objects.oc_petri_net.obj.ObjectCentricPetriNet>`.
Objects of this class can be visualized by calling the corresponding visualization function.

Object-Centric Petri Net Retrieval & Visualization
______________________________________


.. image:: _static/petri_net.png
   :width: 300px
   :align: center

Example of a visualized object-centric Petri net

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
    from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(file_path=filename)
    ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "oc_petri_net.png")

Variant Calculation and Layouting
______________________________________
Equivalent control-flow behavior of process executions are called variants. Since a process execution is a graph, we can find equivalent process executions by annotating each graph's nodes with the activity attribute and finding isomorphic graphs.
OCPA offers two techniques to determine variants: By first calculating lexicographical presentations of the graphs and then refining these (TWO_PHASE), and through one-to-one isomorphism checking (ONE_PHASE). The first is normally faster. One can also choose to
use the approximation of variants through only the lexicographical presentation. This is the default procedure, but can be switched off by passing the right parameter (see example below).
The variant layouting just returns a positioning of chevrons as coordinates. The visualizaiton has to be done using another tool (www.ocpi.ai implements this end-to-end)


.. image:: _static/variant.png
   :width: 500px
   :align: center

A variant visualized with `OCπ <https://ocpi.ai>`_ following the layouting algorithm.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.visualization.log.variants import factory as variants_visualization_factory
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    print("Number of process executions: "+str(len(ocel.process_executions)))
    print("Number of variants: "+str(len(ocel.variants)))
    variant_layouting = variants_visualization_factory.apply(ocel)
    print(variant_layouting[ocel.variants[0]])
