from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
from ocpa.algo.conformance.token_based_replay import algorithm as ocpn_conformance_factory

filename = "../example_logs/jsonocel/simulated-logs.jsonocel"
df = ocel_import_factory.apply(filename)

event_df = df[0]

ocpn = ocpn_discovery_factory.apply(event_df)
gviz = pn_vis_factory.apply(
    ocpn, variant="control_flow", parameters={"format": "svg"})
diag = ocpn_conformance_factory.apply(ocpn,event_df)

parameters = dict()
parameters['act_count']=True
parameters['max_group_size']=True
parameters['min_group_size']=True
parameters['mean_group_size']=True
parameters['median_group_size']=True
parameters['produced_token']=True
parameters['consumed_token']=True
parameters['missing_token']=True
parameters['remaining_token']=True
parameters['arc_freq']=True
parameters['avg_sojourn_time']=True
parameters['med_sojourn_time']=True
parameters['min_sojourn_time']=True
parameters['max_sojourn_time']=True
parameters['format']='svg'

annotated_gviz = pn_vis_factory.apply(
    ocpn, diagnostics=diag, variant="annotated_with_diagnostics", parameters=parameters)
pn_vis_factory.view(annotated_gviz)
