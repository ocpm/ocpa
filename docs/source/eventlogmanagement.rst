Event Log Management
####################

OCPA offers several ways to import object-centric event data. Additionally to the two data formats introduced in the
(`OCEL standard <https://ocel-standard.org>`_) we support the import of CSV files. The importer is the key interface to pass
parameters and settings to the event log. A full description can be found in the :func:`importer's documentation <ocpa.objects.log.importer.csv.factory.apply>`.

Importing CSV Files
___________________

.. code-block:: python

    from ocpa.objects.log.importer.csv import factory as ocel_import_factory
    filename = "sample_logs/csv/BPI2017-Final.csv"
    object_types = ["application", "offer"]
    parameters = {"obj_names":object_types,
                  "val_names":[],
                  "act_name":"event_activity",
                  "time_name":"event_timestamp",
                  "sep":","}
    ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)

Importing JSON OCEL/XML OCEL Files
___________________

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

Importing OCEL 2.0 Files
__________________

There are different formats for OCEL 2.0 files. All of them are extensively documented at the (`OCEL standard <https://www.ocel-standard.org>`_) website.

.. code-block:: python
    from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory
    filename = "sample_logs/ocel2/sqlite/running-example.sqlite"
    ocel = ocel_import_factory.apply(filename)


Exporting JSON OCEL Files
___________________

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    ocel_export_factory.apply(
        ocel, './exported-p2p-normal_export.jsonocel')



Process Execution Extraction & Management
___________________
The technique passed through the parameters determines how process executions will be retrieved for the event log. The
default technique are connected components.
The process executions are extracted upon calling the corresponding property the first time.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    print("Number of process executions: "+str(len(ocel.process_executions)))
    print("Events of the first process execution: "+str(ocel.process_executions[0]))
    print("Objects of the first process execution: "+str(ocel.process_execution_objects[0]))
    print("Process execution graph of the first execution:")
    print(ocel.get_process_execution_graph(0))
    print("Process execution of the first event with event id 0: "+str(ocel.process_execution_mappings[0]))


Import with Parameters
_____________________

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    parameters = {"execution_extraction": "leading_type",
                  "leading_type": "GDSRCPT",
                  "variant_calculation": "two_phase",
                  "exact_variant_calculation":True}
    ocel = ocel_import_factory.apply(filename, parameters = parameters)
    print(len(ocel.variants))
