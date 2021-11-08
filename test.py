import ocpa.objects.eog.retrieval.log as eog_extractor
import ocpa.algo.event_correlation.weakly_connected_components as variant_extractor
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.filtering.log.activity_filtering as activity_filtering
import ocpa.algo.filtering.log.generalization as generalization
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator
from ocpa.visualization.oc_petri_net import factory as pn_vis_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ast import literal_eval
import pandas as pd
# =============================================================================
# =============================================================================
# # log = pd.read_csv("precision_replay_prefix_input.csv",sep=';')
# # object_columns = ["Sales ID","Assembly ID","Shipping ID"]
# # for ot in object_columns:
# #     log[ot] = log[ot].apply(lambda x: "[]" if x!=x else x)
# #     log[ot] = log[ot].apply(literal_eval)
# =============================================================================
# =============================================================================
# =============================================================================
# filename = "example4.csv"
# ots = ["order","item","delivery"]
# event_df = pd.read_csv(filename,sep=';')
# for ot in ots:
#     event_df[ot] = event_df[ot].map(lambda x: [y.strip() for y in x.split(',')] if isinstance(x,str) else [])
# event_df["event_id"] = list(range(0,len(event_df)))
# event_df.index = list(range(0,len(event_df)))
# event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# log = event_df
# object_columns = ots
# =============================================================================

# =============================================================================
# =============================================================================
# # EOG = eog_extractor.from_ocel(log, object_types= object_columns)
# # ocel, variants, v_freq = variant_extractor.from_eog(EOG,log)
# # threshold = 1.0
# # sublog = trace_filtering.filter_infrequent_traces(ocel, threshold, v_freq = v_freq)
# # #sublog = activity_filtering.filter_infrequent_activities(ocel, threshold)
# # #sublog = generalization.generalize(ocel, [(["receiving payment","filing order"],"Bookkeeping"),(["drilling","turning","inspecting"],"Construction")])
# # #sublog = trace_filtering.filter_infrequent_traces(sublog, threshold)
# # ocpn = ocpn_discovery_factory.apply(sublog)
# # contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(sublog, EOG = EOG)
# # #sublog or event log?
# # precision, fitness = precision_fitness_evaluator.apply(sublog,ocpn,contexts=contexts,bindings=bindings)
# # print(precision)
# # print(fitness)
# # gviz = pn_vis_factory.apply(ocpn, variant="control_flow", parameters={"format": "svg", "debug":False})
# # pn_vis_factory.save(gviz,"model_filtered_"+str(threshold) +".svg")
# =============================================================================
# =============================================================================

# remove infrequent activities


# Hilti
# filename = "Hilti_adjusted.csv"
# ots = ["AUFNR","VORGELAGERT","EINKAUF"]
# log = pd.read_csv(filename,sep=';', encoding = "ISO-8859-1")
# object_columns = ots
# for ot in object_columns:
#     log[ot] =log[ot].map(lambda x: [] if x!=x else [x])
# log["event_id"] = list(range(0,len(log)))
# log.index = list(range(0,len(log)))
# log["event_id"] = log["event_id"].astype(float).astype(int)
# print("Read input")
# print(log)
# #generalize production activities
# production_activities = [act for act in log["event_activity"].values.tolist() if act.isdecimal() ]
# sublog = generalization.generalize(log, [(production_activities+["Scheduled start time","Scheduled finish time","Actual finish time","Actual start time"],"Placeholer Production")])
# sublog = activity_filtering.filter_infrequent_activities(sublog, threshold=0.95)


# EOG = eog_extractor.from_ocel(sublog, object_types= object_columns)
# sublog, variants, v_freq = variant_extractor.from_eog(EOG,sublog)


# threshold = 0.8
# sublog = trace_filtering.filter_infrequent_traces(sublog, threshold, v_freq = v_freq)

# #sublog = activity_filtering.filter_infrequent_activities(ocel, threshold)
# #sublog = generalization.generalize(ocel, [(["receiving payment","filing order"],"Bookkeeping"),(["drilling","turning","inspecting"],"Construction")])
# #sublog = trace_filtering.filter_infrequent_traces(sublog, threshold)
# ocpn = ocpn_discovery_factory.apply(log)
# contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(sublog, EOG = EOG)
# #sublog or event log?
# precision, fitness = precision_fitness_evaluator.apply(sublog,ocpn,contexts=contexts,bindings=bindings)
# #print(precision)
# #print(fitness)
# gviz = pn_vis_factory.apply(ocpn, variant="control_flow", parameters={"format": "svg", "debug":False})
# pn_vis_factory.save(gviz,"model_filtered_"+str(threshold) +".svg")


# # =============================================================================
# # =============================================================================
# # # filename = "running_example.csv"
# # # ots = ["orders","items","packages"]
# # # event_df = pd.read_csv(filename,sep=',')
# # # #mask = event_df["event_customers"].apply(lambda v: True if "Gyunam Park" in v else False)
# # # #mask2 = event_df["event_products"].apply(lambda v: True if "iPad" in v else False)
# # # #mask3 = event_df["event_products"].apply(lambda v: True if "MacBook Air" in v else False)
# # # #event_df = event_df[mask & mask2 &mask3]
# # # print(event_df)
# # # for ot in ots:
# # #     event_df[ot] = event_df[ot].apply(lambda x: "[]" if x!=x else x)
# # #     event_df[ot] = event_df[ot].apply(literal_eval)
# # #     #event_df[ot] = event_df[ot].map(lambda x: [y.strip() for y in x.split(',')] if isinstance(x,str) else [])
# # # event_df["event_id"] = list(range(0,len(event_df)))
# # # event_df.index = list(range(0,len(event_df)))
# # # event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# # # log = event_df
# # # object_columns = ots
# # # #print(log)
# # #
# # # #generalize production activities
# # # #production_activities = [act for act in log["event_activity"].values.tolist() if act.isdecimal() ]
# # # #sublog = generalization.generalize(log, [(production_activities+["Scheduled start time","Scheduled finish time","Actual finish time","Actual start time"],"Placeholer Production")])
# # # #sublog = activity_filtering.filter_infrequent_activities(sublog, threshold=0.95)
# # #
# # # print("Extract object graph")
# # # EOG = eog_extractor.from_ocel(log, object_types= object_columns)
# # # print("Calculate Variants")
# # # sublog, variants, v_freq = variant_extractor.from_eog(EOG,log)
# # # print(len(variants))
# # #
# # #
# # # threshold = 0.1
# # # print("filter traces")
# # # sublog = trace_filtering.filter_infrequent_traces(sublog, threshold, v_freq = v_freq)
# # #
# # # #sublog = activity_filtering.filter_infrequent_activities(ocel, threshold)
# # # #sublog = generalization.generalize(ocel, [(["receiving payment","filing order"],"Bookkeeping"),(["drilling","turning","inspecting"],"Construction")])
# # # #sublog = trace_filtering.filter_infrequent_traces(sublog, threshold)
# # # ocpn = ocpn_discovery_factory.apply(sublog)
# # # contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(sublog, EOG = EOG)
# # # #sublog or event log?
# # # precision, fitness = precision_fitness_evaluator.apply(log,ocpn,contexts=contexts,bindings=bindings)
# # # print(precision)
# # # print(fitness)
# # # gviz = pn_vis_factory.apply(ocpn, variant="control_flow", parameters={"format": "svg", "debug":False})
# # # pn_vis_factory.save(gviz,"running_example_model_filtered_"+str(threshold) +".svg")
# # =============================================================================
# # =============================================================================
