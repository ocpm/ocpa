from ocpa.algo.ocel2_use_cases.object_change_tables import plot_attribute_over_time
from ocpa.objects.log.importer.ocel2.sqlite import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
from ocpa.algo.predictive_monitoring import tabular
ocel = ocel_import_factory.apply("../../sample_logs/ocel2/sqlite/logistics.sqlite")
print(len(ocel.process_executions))
print(len(ocel.o2o_graph.graph.nodes()))
print(len(ocel.log.log))
ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
ocpn_vis_factory.view(gviz)
activities = list(set(ocel.log.log["event_activity"].tolist()))
feature_set = [(predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ()),
               (predictive_monitoring.EVENT_POOLING_TIME, ("Container",))]  + [(predictive_monitoring.EVENT_ACTIVITY, (act,))
     for act in activities]
feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
table = tabular.construct_table(
    feature_storage)
print(table)
for act in activities:
    filtered_table = table[table[(predictive_monitoring.EVENT_ACTIVITY, (act,))]==1]
    print("_________")
    print("For activity "+act+":")
    print("Average Synchronization time: "+str(filtered_table[(predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ())].mean()))
    print("Average Pooling time for container: " + str(
        filtered_table[(predictive_monitoring.EVENT_POOLING_TIME, ("Container",))].mean()))
    print("_________")