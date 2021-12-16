import time

from ocpa.objects.log.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import pandas as pd
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator
import ocpa.visualization.oc_petri_net.factory as vis_factory
import ocpa.visualization.log.variants.factory as log_viz
import ocpa.objects.log.importer.ocel.factory as import_factory
# TODO: Preprocessing and conversion from other types of OCEL
# filepath = "running-example.jsonocel"
# df = import_factory.apply(filepath, parameters={"return_df":True})
# print(df[0])
# print(df[0].dtypes)
# f_ocel = OCEL(df[0])
# print(f_ocel.object_types)
# #ocpn = ocpn_discovery_factory.apply(f_ocel, parameters={"debug": False})
# exit
#
# filepath = "running-example.xmlocel"
# df = import_factory.apply(filepath,import_factory.OCEL_XML, parameters={"return_df":True})
# print(df[0])
# print(df[0].dtypes)
# f_ocel = OCEL(df[0])
# print(f_ocel.object_types)
# #ocpn = ocpn_discovery_factory.apply(f_ocel, parameters={"debug": False})
# exit




filename = "BPI2017.csv"
ots = ["application", "offer"]


event_df = pd.read_csv(filename, sep=',')[:25]
print(event_df)
for ot in ots:
    event_df[ot] = event_df[ot].map(
        lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
event_df["event_id"] = list(range(0, len(event_df)))
event_df.index = list(range(0, len(event_df)))
event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
ocel = OCEL(event_df, ots)
t_start = time.time()
print("Number of cases: "+str(len(ocel.cases)))
print("Number of variants: "+str(len(ocel.variants)))
print(str(time.time()-t_start))
print(ocel.variant_frequency)
print(ocel.log)
t_start = time.time()
vars = log_viz.apply(ocel)
print(str(time.time()-t_start))
#print(vars)
#sub_ocel = trace_filtering.filter_infrequent_traces(ocel, 0.3)
#ocpn = ocpn_discovery_factory.apply(sub_ocel, parameters={"debug": False})
#contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(ocel)
#precision, fitness = precision_fitness_evaluator.apply(
#    ocel, ocpn, contexts=contexts, bindings=bindings)
#print("Precision: "+str(precision))
#print("Fitness: "+str(fitness))

