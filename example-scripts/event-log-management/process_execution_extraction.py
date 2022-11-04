from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
print("Number of process executions: "+str(len(ocel.process_executions)))
print("Events of the first process execution: " +
      str(ocel.process_executions[0]))
print("Objects of the first process execution: " +
      str(ocel.process_execution_objects[0]))
print("Process execution graph of the first execution:")
print(ocel.get_process_execution_graph(0))
print("Process execution of the first event with event id 0: " +
      str(ocel.process_execution_mappings[0]))
