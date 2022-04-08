import time

import matplotlib.pyplot as plt

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
from ocpa.algo.feature_extraction import tabular
from datetime import date, timedelta
from statsmodels.tsa.stattools import grangercausalitytests
import statsmodels.tools.sm_exceptions as stats_exceptions
import ruptures as rpt
import numpy as np
import seaborn as sns
from statistics import median as median
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

def avg(x):
    if len(x) == 0:
        return np.nan
    return sum(x)/len(x)

def std_dev(x):
    m = sum(x) / len(x)
    return sum((xi - m) ** 2 for xi in x) / len(x)

filename = "example_logs/mdl/BPI2017-Full-MDL.csv"
ots = ["application", "offer"]


event_df = pd.read_csv(filename, sep=',')[:200]
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
event_df["event_start_timestamp"] = pd.to_datetime(event_df["event_start_timestamp"])
ocel = OCEL(event_df, ots)
t_start = time.time()
print("Number of process executions: "+str(len(ocel.cases)))
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

F = [(feature_extraction.EVENT_NUM_OF_OBJECTS,()),(feature_extraction.EVENT_TYPE_COUNT,("offer",))]
feature_storage = feature_extraction.apply(ocel,F,[])
tabular.construct_table(feature_storage)


# #######EXAMPLE
# if False:
#     explainable_drifts = []
#     p=0.05
#     s, time_index = time_series.construct_time_series(ocel,timedelta(days=7),[],[],ocpa.algo.filtering.log.time_filtering.start)
#     print(s)
#     loc = {k:[bp for bp in rpt.Pelt().fit(s[k]/np.max(s[k])).predict(pen=0.2)] for k in s.keys()}
#     print(loc)
#     phi_1 = lambda x:x
#     phi_2 = lambda x:x
#     for feat_1 in s.keys():
#         for feat_2 in s.keys():
#             if feat_1== feat_2:
#                 continue
#             loc_1 = loc[feat_1]
#             loc_2 = loc[feat_2]
#             for d in loc_1:
#                 for d_ in loc_2:
#                     if d_ < d:
#                         #Granger test
#                         try:
#                             res = grangercausalitytests(pd.DataFrame({feat_1:s[feat_1],feat_2:s[feat_2]}),[d-d_])
#                         except ValueError:
#                             #insufficient observations are not added
#                             continue
#                         #print(res)
#                         p_value = res[d-d_][0]['ssr_ftest'][1]
#                         if p_value <= p:
#                             explainable_drifts.append((feat_1,feat_2,d,d_,p_value))
#
#     print(explainable_drifts)
#
#
#     # ###Visualization
#     data_df = pd.DataFrame({k:s[k] for k in s.keys()})
#     viz_df = pd.concat([pd.DataFrame({"date":time_index}), data_df], axis=1)
#     viz_df.set_index('date', inplace=True)
#     sns.set_style("darkgrid")
#     sns.lineplot(data = viz_df)
#     plt.savefig("time_series_example.png")
#
#     for feat in s.keys():
#         plt.clf()
#         data_df = pd.DataFrame({feat:s[feat]})
#         viz_df = pd.concat([pd.DataFrame({"date":time_index}), data_df], axis=1)
#         viz_df.set_index('date', inplace=True)
#         sns.set_style("darkgrid")
#         sns.lineplot(data = viz_df)
#         plt.savefig("time_series_example"+feat[1][0]+".png")
# #######EXAMPLE OVER
#
#
#
# #Visualizing different inclusion functions
# if True:
#     feat_to_s = {}
#     for f_in in [ocpa.algo.filtering.log.time_filtering.start, ocpa.algo.filtering.log.time_filtering.end, ocpa.algo.filtering.log.time_filtering.contained, ocpa.algo.filtering.log.time_filtering.spanning, ocpa.algo.filtering.log.time_filtering.events]:
#         s_time= time.time()
#         s, time_index = time_series.construct_time_series(ocel, timedelta(days=7),
#                                                           [(avg, (feature_extraction.EVENT_NUM_OF_OBJECTS,()))],
#                                                           [(
#                                                           avg,
#                                                           (feature_extraction.EXECUTION_THROUGHPUT,()))],
#                                                           f_in)
#         print("total time series: " + str(time.time() - s_time))
#         for feat in s.keys():
#             if feat not in feat_to_s.keys():
#                 feat_to_s[feat] = []
#             feat_to_s[feat].append((f_in.__name__, s[feat], time_index))
#     for feat in feat_to_s.keys():
#         plt.clf()
#         sns.set(rc={'figure.figsize': (24, 8)})
#         plt.rcParams["axes.labelsize"] = 12
#         plt.rcParams["axes.titlesize"] = 14
#         data_df = pd.DataFrame({f_in_name: s for (f_in_name, s, time_index) in feat_to_s[feat]})
#         viz_df = pd.concat([pd.DataFrame({"date": feat_to_s[list(feat_to_s.keys())[0]][0][2]}), data_df], axis=1)
#         viz_df.set_index('date', inplace=True)
#         sns.set_style("darkgrid")
#         plot_ = sns.lineplot(data=viz_df)
#         for index, label in enumerate(plot_.get_xticklabels()):
#             if index % 2 == 0:
#                 label.set_visible(True)
#             else:
#                 label.set_visible(False)
#         plot_.set_title("Time Series for " + "Different Inclusion Functions")
#         plot_.set_ylabel("Average throughput time in s" if feat[1][0] == "exec_throughput" else "Average number of objects per event")
#         plot_.set_xlabel(
#             "Date")
#         plt.savefig("Inclusion_function_comparison_feature_" + feat[1][0] +".png",dpi=600)
#
# #Visualizing different window sizes
# if True:
#     feat_to_s = {}
#     window_array = [28,6,1,7]#[1,3,7,30]
#     for w in window_array:
#         s, time_index = time_series.construct_time_series(ocel, timedelta(days=w),
#                                                           [],
#                                                           [(avg,
#                                                             (feature_extraction.EXECUTION_THROUGHPUT,()))],
#                                                           ocpa.algo.filtering.log.time_filtering.start)
#         for feat in s.keys():
#             if feat not in feat_to_s.keys():
#                 feat_to_s[feat] = []
#             feat_to_s[feat].append((str(w)+" days", s[feat], time_index))
#     for w in window_array:
#         s, time_index = time_series.construct_time_series(ocel, timedelta(days=w),
#                                                           [(avg,
#                                                             (feature_extraction.EVENT_NUM_OF_OBJECTS,()))],
#                                                           [],
#                                                           ocpa.algo.filtering.log.time_filtering.events)
#         for feat in s.keys():
#             if feat not in feat_to_s.keys():
#                 feat_to_s[feat] = []
#             feat_to_s[feat].append((str(w)+" days", s[feat], time_index))
#     viz_df = pd.DataFrame()
#
#     for feat in feat_to_s.keys():
#         data_df = pd.DataFrame()
#         plt.clf()
#         sns.set(rc={'figure.figsize': (24, 8)})
#         plt.rcParams["axes.labelsize"] = 12
#         plt.rcParams["axes.titlesize"] = 14
#         for (w, s, time_index) in feat_to_s[feat]:
#             if (w=="1 days"):
#                 data_df["date"] = time_index
#                 data_df.set_index("date",inplace=True)
#         for (w, s, time_index) in feat_to_s[feat]:
#             for i in range(0,len(s)):
#                 if s[i] > 0.001:
#                     data_df.loc[time_index[i],w] = s[i]
#             #data_df.loc[time_index] = s
#             #frame = pd.DataFrame({"date":time_index,w:s})
#             #frame.set_index("date")
#             #data_df = data_df.join(frame,how='left')
#             print(data_df)
#         #for (w, s, time_index) in feat_to_s[feat]:
#         #    data_df = pd.concat([data_df,pd.DataFrame({w:s})], axis=1)
#         #data_df = pd.DataFrame({w: s for (w, s, time_index) in feat_to_s[feat]})
#         #for (w, s, time_index) in feat_to_s[feat]:
#         #    if (w=="1 days"):
#         #        viz_df = pd.concat([pd.DataFrame({"date": time_index}), data_df], axis=1)
#         #viz_df.set_index('date', inplace=True)
#         sns.set_style("darkgrid")
#         print(data_df)
#         plot_ = sns.lineplot(data=data_df)
#         for index, label in enumerate(plot_.get_xticklabels()):
#             if index % 2 == 0:
#                 label.set_visible(True)
#             else:
#                 label.set_visible(False)
#         plot_.set_title("Time Series for " + "Different Window Sizes")
#         plot_.set_ylabel("Average throughput time in s" if feat[1][0] == "exec_throughput" else "Average number of objects per event")
#         plot_.set_xlabel(
#             "Date")
#         plt.savefig("Window_size_comparison_feature_" + feat[1][0]  + ".png",dpi=600)
#
#
#
#
#
#
#     # for feat in s.keys():
#     #     plt.clf()
#     #     data_df = pd.DataFrame({feat: s[feat]})
#     #     viz_df = pd.concat([pd.DataFrame({"date": time_index}), data_df], axis=1)
#     #     viz_df.set_index('date', inplace=True)
#     #     sns.set_style("darkgrid")
#     #     sns.lineplot(data=viz_df)
#     #     plt.savefig("time_series" + feat[1] +"_"+f_in.__name__+ ".png")
#
# #Scalability
# if True:
#     feature_array = [(avg,(feature_extraction.EXECUTION_THROUGHPUT,())),(sum, (feature_extraction.EXECUTION_IDENTITY,())),(avg, (feature_extraction.EXECUTION_FEATURE,("event_RequestedAmount",))),(std_dev, (feature_extraction.EXECUTION_FEATURE,("event_RequestedAmount",))),(max, (feature_extraction.EXECUTION_FEATURE,("event_RequestedAmount",))),(sum, (feature_extraction.EXECUTION_FEATURE,("event_RequestedAmount",))),(avg, (feature_extraction.EXECUTION_FEATURE,("event_RequestedAmount",))),      (avg, (feature_extraction.EXECUTION_FEATURE,("event_OfferedAmount",))),(std_dev, (feature_extraction.EXECUTION_FEATURE,("event_OfferedAmount",))),(max, (feature_extraction.EXECUTION_FEATURE,("event_OfferedAmount",))),(sum, (feature_extraction.EXECUTION_FEATURE,("event_OfferedAmount",))),(avg, (feature_extraction.EXECUTION_FEATURE,("event_OfferedAmount",))),(avg, (feature_extraction.EXECUTION_SERVICE_TIME,("event_start_timestamp",))),(std_dev, (feature_extraction.EXECUTION_SERVICE_TIME,("event_start_timestamp",))),(sum, (feature_extraction.EXECUTION_SERVICE_TIME,("event_start_timestamp",))),(max, (feature_extraction.EXECUTION_SERVICE_TIME,("event_start_timestamp",))),(median, (feature_extraction.EXECUTION_SERVICE_TIME,("event_start_timestamp",))),(avg, (feature_extraction.EXECUTION_AVG_SERVICE_TIME,("event_start_timestamp",))),(max, (feature_extraction.EXECUTION_AVG_SERVICE_TIME,("event_start_timestamp",))),(std_dev, (feature_extraction.EXECUTION_AVG_SERVICE_TIME,("event_start_timestamp",))),(avg,(feature_extraction.EXECUTION_NUM_OBJECT,())), (avg,(feature_extraction.EXECUTION_NUM_OF_STARTING_EVENTS,())), (avg,(feature_extraction.EXECUTION_NUM_OF_EVENTS,())), (avg,(feature_extraction.EXECUTION_UNIQUE_ACTIVITIES,())),(median,(feature_extraction.EXECUTION_THROUGHPUT,())),(max,(feature_extraction.EXECUTION_NUM_OBJECT,())), (sum,(feature_extraction.EXECUTION_NUM_OF_STARTING_EVENTS,())), (sum,(feature_extraction.EXECUTION_NUM_OF_EVENTS,())),(avg,(feature_extraction.EXECUTION_UNIQUE_ACTIVITIES,())), (max,(feature_extraction.EXECUTION_UNIQUE_ACTIVITIES,())), (median,(feature_extraction.EXECUTION_UNIQUE_ACTIVITIES,())), (max,(feature_extraction.EXECUTION_NUM_OF_END_EVENTS,())), (avg,(feature_extraction.EXECUTION_NUM_OF_END_EVENTS,())), (max,(feature_extraction.EXECUTION_LAST_EVENT_TIME_BEFORE,())), (avg,(feature_extraction.EXECUTION_LAST_EVENT_TIME_BEFORE,())),(std_dev,(feature_extraction.EXECUTION_THROUGHPUT,())), (std_dev,(feature_extraction.EXECUTION_LAST_EVENT_TIME_BEFORE,())),(max,(feature_extraction.EXECUTION_THROUGHPUT,()))]
#     times = {}
#     explainable_drifts = []
#     p=0.01
#     for l in range(1,len(feature_array)):
#         #Time Series Extraction
#         s_time = time.time()
#         s, time_index = time_series.construct_time_series(ocel, timedelta(days=7),[],feature_array[:l+1],ocpa.algo.filtering.log.time_filtering.start)
#         extraction_time = time.time()-s_time
#         #Concept Drift Detection
#         s_time = time.time()
#         loc = {k: [bp for bp in rpt.Pelt().fit(s[k] / np.max(s[k])).predict(pen=0.05)] for k in s.keys()}
#         #print(loc)
#         detection_time = time.time() - s_time
#
#         #Cause-Effect
#         s_time = time.time()
#         phi_1 = lambda x:x
#         phi_2 = lambda x:x
#         for feat_1 in s.keys():
#             for feat_2 in s.keys():
#                 if feat_1== feat_2:
#                     continue
#                 loc_1 = loc[feat_1]
#                 loc_2 = loc[feat_2]
#                 for d in loc_1:
#                     for d_ in loc_2:
#                         if d_ < d:
#                             #Granger test
#                             try:
#                                 res = grangercausalitytests(pd.DataFrame({feat_1:s[feat_1],feat_2:s[feat_2]}),[d-d_])
#                             except (ValueError, stats_exceptions.InfeasibleTestError ) as err:
#                                 #insufficient observations are not added
#                                 continue
#                             #print(res)
#                             p_value = res[d-d_][0]['ssr_ftest'][1]
#                             if p_value <= p:
#                                 explainable_drifts.append((feat_1,feat_2,d,d_,p_value))
#
#         correlation_time = time.time() - s_time
#         time_vector = [extraction_time,detection_time,correlation_time]
#         all_times = sum(time_vector)
#         times[l+1] = [all_times] + time_vector
#         print(str(l+1)+" features:")
#         print(times[l+1])
#         print(explainable_drifts)
#     print(times)
#     plt.clf()
#     time_df = pd.DataFrame.from_dict(times,orient='index',columns = ["Total Time","Extraction Time","Concept Drift Detection","Granger Causality"])
#     #time_df.set_index("Number of Features", inplace=True)
#     print(time_df)
#     sns.set_style("darkgrid")
#     plot_ = sns.lineplot(data=time_df)
#     plot_.set_title("Runtime for Different Number of Features")
#     plot_.set_ylabel("Runtime in s")
#     plot_.set_xlabel("Number of Features")
#     plt.savefig("Runtimes_framework_comparison.png",dpi=600)
# # feature_storage = feature_extraction.apply(ocel,[feature_extraction.EVENT_NUM_OF_OBJECTS],[feature_extraction.EXECUTION_NUM_OF_EVENTS,feature_extraction.EXECUTION_NUM_OF_END_EVENTS])
# #
# #
# # ####example of how the feature storage looks like
# # for f_g in feature_storage.feature_graphs:
# #     print("Next Feature Graph")
# #     for e in f_g.edges:
# #         print("Edge: from "+str(e.source)+" to "+str(e.target)+" with objects "+str(e.objects))
# #     print("Execution (global) attributes:")
# #     print(f_g.attributes)
# #     print("Event attributes:")
# #     for n in f_g.nodes:
# #         print("for event: "+str(n.event_id))
# #         print(n.attributes)
# #         print(n.objects)
