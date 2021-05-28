from oppa.objects.log.importer.ocel import factory as ocel_import_factory
from oppa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from oppa.visualization.oc_petri_net import factory as pn_vis_factory

filename = "../example_logs/jsonocel/simulated-logs.jsonocel"
# log = ocel.import_log(filename)
# print(ocel.get_events(log))
df = ocel_import_factory.apply(filename)

event_df = df[0]
print(event_df)

ocpn = ocpn_discovery_factory.apply(event_df)
gviz = pn_vis_factory.apply(
    ocpn, variant="control_flow", parameters={"format": "svg"})

# print(gviz)
pn_vis_factory.view(gviz)
