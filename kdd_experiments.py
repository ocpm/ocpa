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




# filename = "BPI2017.csv"
# ots = ["application", "offer"]
#
#
# event_df = pd.read_csv(filename, sep=',')[:200000]
# print(event_df)
# for ot in ots:
#     event_df[ot] = event_df[ot].map(
#         lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
# event_df["event_id"] = list(range(0, len(event_df)))
# event_df.index = list(range(0, len(event_df)))
# event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# ocel = OCEL(event_df, ots)
# t_start = time.time()
# print("Number of cases: "+str(len(ocel.cases)))
# print(str(time.time()-t_start))
# t_start = time.time()
# print("Number of variants: "+str(len(ocel.variants)))
# print(str(time.time()-t_start))
# print(ocel.variant_frequency)
# #print(ocel.log)
# t_start = time.time()
# vars = log_viz.apply(ocel)
# print(str(time.time()-t_start))


######Datasets
datasets = ["example_logs/mdl/Full_slim_minimal.csv"]
types = [["application", "offer"]]

########## Extraction running times
#Basic statistics for the five event data sets
for i in range(0,len(datasets)):
    ds = datasets[i]
    ts = types[i]
    if ds.endswith(".csv"):
        event_df = pd.read_csv(ds)
        for t in ts:
            event_df[t] = event_df[t].map(
                lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
        event_df["event_id"] = list(range(0, len(event_df)))
        event_df.index = list(range(0, len(event_df)))
        event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
        execution_extraction_parameters = [("weakly","")] + [("leading",t) for t in ts]
        for technique, t in execution_extraction_parameters:
            s_time = time.time()
            print(technique +" "+ t)
            ocel = OCEL(event_df, ts, execution_extraction=technique,leading_object_type=t)
            print("Number of cases: "+str(len(ocel.cases)))
            sum_lengths = 0
            max_length = 0
            min_length = 10000000
            sum_obs = 0
            max_obs = 0
            min_obs = 10000000
            for i in range(0,len(ocel.cases)):
                exec = ocel.cases[i]
                num_events = len(exec)
                if num_events  > max_length:
                    max_length = num_events
                if min_length  > num_events:
                    min_length = num_events
                sum_lengths += num_events
                case_obs = ocel.case_objects[i]
                num_obs = len(case_obs)
                if num_obs > max_obs:
                    max_obs = num_obs
                if min_obs > num_obs:
                    min_obs = num_obs
                sum_obs += num_obs
            avg_length = sum_lengths/len(ocel.cases)
            avg_obs = sum_obs/ len(ocel.cases)
            print("Max length: "+str(max_length))
            print("Min length: " + str(min_length))
            print("Avg length: " + str(avg_length))
            print("Max objects: " + str(max_obs))
            print("Min objects: " + str(min_obs))
            print("Avg objects: " + str(avg_obs))
            print("Took: "+str(time.time()-s_time))
            #get execution times
            print(technique + " " + t)
            for t_dev in range(1,10):
                log_size = int(len(event_df)/10*t_dev)
                print("___________")
                print("For size" +str(log_size))
                s_time = time.time()
                ocel = OCEL(event_df[:log_size], ts, execution_extraction=technique, leading_object_type=t)
                print("Number of cases: " + str(len(ocel.cases)))
                print("Took: " + str(time.time() - s_time))
                #print("Number of cases: " + str(len(ocel.cases)))


#Running times of extraction for different subsizes of each log and for different extraction techniques




######### Isomorphism times
#calculate number of variants for first and second step for all logs,

#calculate comparison numbers for number of classes and running tim efrom naive baseline



######## Visualization