Event Log Management
####################

OCPA offers several ways to import object-centric event data. Additionally to the two data formats introduced in the
(`OCEL standard <www.ocel-standard.org>`_) we support the import of CSV files. The importer is the key interface to pass
parameters and settings to the event log. A full description can be found in the :func:`importer's documentation <ocpa.objects.log.importer.csv.factory.apply>`.

Importing CSV Files
___________________

.. code-block:: python

    import ocpa
    from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
    object_types = ["application", "offer"]
    parameters = {"obj_names":object_types,
                  "val_names":[],
                  "act_name":"event_activity",
                  "time_name":"event_timestamp",
                  "sep":",",
                  "execution_extraction":ocpa.algo.util.process_executions.factory.LEAD_TYPE,
                  "leading_type":object_types[0],
                  "variant_calculation":ocpa.algo.util.variants.factory.TWO_PHASE}
    ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)

Importing JSON OCEL/XML OCEL Files
___________________

.. code-block:: python

    import ocpa
    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    filename = "<path-to-your-file>"
    parameters = {}
    ocel = ocel_import_factory.apply(filename,parameters)

Exporting JSON OCEL Files
___________________

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
    filename = "<path-to-your-file>"
    ocel = ocel_import_factory.apply(filename)
    ocel_export_factory.apply(ocel, '<path-to-save-ocel>')



Process Execution Extraction & Management
___________________
The technique passed through the parameters determines how process executions will be retrieved for the event log. The
default technique are connected components.
The process executions are extracted upon calling the corresponding property the first time.

.. code-block:: python

    from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
    object_types = ["application", "offer"]
    parameters = {"obj_names":object_types,
                  "val_names":[],
                  "act_name":"event_activity",
                  "time_name":"event_timestamp",
                  "sep":",",}
    ocel = ocel_import_factory.apply(file_path= filename,parameters = parameters)
    print("Number of process executions: "+str(len(ocel.process_executions)))
    print("Events of the first process execution: "+str(ocel.process_executions[0]))
    print("Objects of the first process execution: "+str(ocel.process_execution_objects[0]))
    print("Process execution of the first event with event id 0: "+str(ocel.process_execution_mappings[0]))

