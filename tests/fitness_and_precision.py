import ocpa.objects.log.importer.ocel.factory as ocel_import_factory
import ocpa.algo.discovery.ocpn.algorithm as discovery_factory
import ocpa.algo.evaluation.precision_and_fitness.evaluator as evaluation_factory
from ocpa.objects.log.obj import OCEL
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
import ocpa.algo.reduction.ocpn.algorithm as reduction_factory
import ocpa.objects.log.converter.factory as convert_factory

# Converting XMLOCEL -> JSONOCEL
# ocel_log = ocel.import_log("log.xmlocel")
# ocel.export_log(ocel_log,'log.jsonocel')

df, _ = ocel_import_factory.apply(
    f"log.jsonocel", parameters={'return_df': True})

# ocel = ocel_import_factory.apply(
#     f"log.jsonocel")
# df = convert_factory.apply(ocel, variant='json_to_mdl')

ocel_obj = OCEL(df)

ocpn = discovery_factory.apply(ocel_obj)

gviz = pn_vis_factory.apply(
    ocpn, variant="control_flow", parameters={"format": "svg"})
pn_vis_factory.view(gviz)

precision, fitness = evaluation_factory.apply(ocel_obj, ocpn)
print(f"Precision: {precision}, Fitness: {fitness}")
