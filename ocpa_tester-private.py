import time

import ocpa.algo.filtering.log.time_filtering
from ocpa.objects.log.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import pandas as pd
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator
import ocpa.visualization.oc_petri_net.factory as vis_factory
import ocpa.visualization.log.variants.factory as log_viz
import ocpa.objects.log.importer.ocel.factory as import_factory
import ocpa.algo.feature_extraction.factory as feature_extraction
from ocpa.algo.feature_extraction import time_series
from datetime import date, timedelta
from statsmodels.tsa.stattools import grangercausalitytests
import ruptures as rpt
import numpy as np
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




filename = "example_logs/mdl/BPI2017-Full-MDL.csv"
ots = ["application", "offer"]


event_df = pd.read_csv(filename, sep=',')[:10000]
event_df["event_timestamp"] = pd.to_datetime(event_df["event_timestamp"])



# filename = "example_logs/jsonxml/DS2.jsonocel"
# event_df = import_factory.apply(filename,import_factory.OCEL_JSON, parameters={"return_df": True})[0]#[:2000]
# ots = ["items","orders","packages"]
# for t in ots:
#     event_df.loc[event_df[t].isnull(), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
# event_df["event_timestamp"] = pd.to_datetime(event_df["event_timestamp"])


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
#print("Number of variants: "+str(len(ocel.variants)))
print(str(time.time()-t_start))
#print(ocel.variant_frequency)
print(ocel.log)
#t_start = time.time()
#vars = log_viz.apply(ocel)
#print(str(time.time()-t_start))
#print(vars)
#sub_ocel = trace_filtering.filter_infrequent_traces(ocel, 0.3)
#ocpn = ocpn_discovery_factory.apply(sub_ocel, parameters={"debug": False})
#contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(ocel)
#precision, fitness = precision_fitness_evaluator.apply(
#    ocel, ocpn, contexts=contexts, bindings=bindings)
#print("Precision: "+str(precision))
#print("Fitness: "+str(fitness))
p=0.05
s = time_series.construct_time_series(ocel,timedelta(days=1),[(max,feature_extraction.EVENT_NUM_OF_OBJECTS)],[(lambda x: sum(x)/len(x), feature_extraction.EXECUTION_NUM_OF_EVENTS)],ocpa.algo.filtering.log.time_filtering.spanning)
print(s)
loc = {k:[bp for bp in rpt.Pelt().fit(s[k]/np.max(s[k])).predict(pen=0.5)] for k in s.keys()}
print(loc)
phi_1 = lambda x:x
phi_2 = lambda x:x
for feat_1 in s.keys():
    for feat_2 in s.keys():
        if feat_1== feat_2:
            continue
        loc_1 = loc[feat_1]
        loc_2 = loc[feat_2]
        for d in loc_1:
            for d_ in loc_2:
                if d_ < d:
                    #Granger test
                    res = grangercausalitytests(pd.DataFrame({feat_1:s[feat_1],feat_2:s[feat_2]}),[d-d_])
                    #print(res)
                    p_value = res[d-d_][0]['ssr_ftest'][1]
                    print(p_value)
# feature_storage = feature_extraction.apply(ocel,[feature_extraction.EVENT_NUM_OF_OBJECTS],[feature_extraction.EXECUTION_NUM_OF_EVENTS,feature_extraction.EXECUTION_NUM_OF_END_EVENTS])
#
#
# ####example of how the feature storage looks like
# for f_g in feature_storage.feature_graphs:
#     print("Next Feature Graph")
#     for e in f_g.edges:
#         print("Edge: from "+str(e.source)+" to "+str(e.target)+" with objects "+str(e.objects))
#     print("Execution (global) attributes:")
#     print(f_g.attributes)
#     print("Event attributes:")
#     for n in f_g.nodes:
#         print("for event: "+str(n.event_id))
#         print(n.attributes)
#         print(n.objects)
