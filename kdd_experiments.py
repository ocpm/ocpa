import itertools
import random
import time

from ocpa.objects.log.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import pandas as pd
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator
import ocpa.visualization.oc_petri_net.factory as vis_factory
import ocpa.visualization.log.variants.factory as log_viz
import ocpa.algo.filtering.log.case_filtering as execution_filtering
import ocpa.objects.log.importer.ocel.factory as import_factory
import matplotlib.pyplot as plt
import seaborn as sns
from multiprocessing.dummy import Pool as ThreadPool
sns.set(style='ticks', palette='Set2')
sns.despine()

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
datasets = ["example_logs/mdl/Full_slim_minimal.csv","example_logs/jsonxml/running-example.jsonocel","example_logs/mdl/incident_ocel.csv","example_logs/mdl/BPI_2018_2017.csv"]
###datasets = ["example_logs/mdl/Full_slim_minimal.csv","example_logs/mdl/BPI_2018_2017.csv"]
#Here are som eproblems with respect to purchase as leading object type, the first 10 percent of th elog does not contain any purchase, i.e., producing division by zero error
#datasets = ["example_logs/mdl/BPI2019.csv"]
types = [["application", "offer"],["items","orders","packages"],["incident","customer"],["Payment application","Control summary","Entitlement application","Geo parcel document","Inspection","Reference alignment"]]
###types = [["application", "offer"],["Payment application","Control summary","Entitlement application","Geo parcel document","Inspection","Reference alignment"]]
#types = [["Purchase","Item"]]

########## Extraction running times
#Basic statistics for the five event data sets
x = False
if x:
    running_times = {}
    for i in range(0,len(datasets)):
        ds = datasets[i]
        print("_____________")
        print(ds)
        print("_____________")
        ts = types[i]
        event_df = None
        if ds.endswith(".csv"):
            event_df = pd.read_csv(ds)
            print(event_df)
            for t in ts:
                event_df[t] = event_df[t].map(
                    lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
            event_df["event_id"] = list(range(0, len(event_df)))
            event_df.index = list(range(0, len(event_df)))

        elif ds.endswith(".jsonocel"):
            event_df = import_factory.apply(ds,import_factory.OCEL_JSON, parameters={"return_df": True})[0]
            for t in ts:
                event_df.loc[event_df[t].isnull(),[t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
        event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
        execution_extraction_parameters = [("weakly","")] + [("leading",t) for t in ts]
        for technique, t in execution_extraction_parameters:
            s_time = time.time()
            print(technique +" "+ t)
            ocel = OCEL(event_df, ts, execution_extraction=technique,leading_object_type=t)
            print("Number of cases: "+str(len(ocel.cases)))
            r_full_time = time.time() - s_time
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
            running_times[(ds, technique, t)] = []

            for t_dev in range(1,10):
                log_size = int(len(event_df)/10*t_dev)
                print("___________")
                print("For size" +str(log_size))
                s_time = time.time()
                ocel = OCEL(event_df[:log_size], ts, execution_extraction=technique, leading_object_type=t)
                print("Number of cases: " + str(len(ocel.cases)))
                print("Took: " + str(time.time() - s_time))
                r_time = time.time() - s_time
                running_times[(ds, technique, t)].append((log_size, r_time))
                #print("Number of cases: " + str(len(ocel.cases)))
            running_times[(ds, technique, t)].append((len(event_df), r_time))
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
    color_map = {datasets[0]:colors[0],datasets[1]:colors[1],datasets[2]:colors[2],datasets[3]:colors[3]}
    symbols = [None,"o","v",".","^","<",">"]
    sns.set(rc={'figure.figsize':(24,8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9,5))
    for ds_ in datasets:
        #plt.clf()
        for (ds,technique,t) in running_times.keys():
            if ds != ds_:
                continue
            ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
            pointer_map = {ext_params[i]:symbols[i] for i in range(0,len(ext_params))}
            x = [elem[0] for elem in running_times[(ds,technique,t)]]
            y = [elem[1] for elem in running_times[(ds,technique,t)]]
            sns.lineplot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)], label="DS"+str(datasets.index(ds_)+1)+" "+t)
            #plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Events")
    plt.ylabel("Running Time of Extraction in s")
    plt.title("Running Time of Execution Extraction")
    plt.tight_layout()

    plt.savefig("extr_sns_full"+".png")

print("______________")
print("______________")
print("Isomorphism comparison")
print("______________")
print("______________")


def scalability_iso(ind, datasets, types):
    random.seed(a=33)
    running_times = {}
    # Running times of extraction for different subsizes of each log and for different extraction techniques
    i = ind
    ds = datasets[i]
    print("_____________")
    print(ds)
    print("_____________")
    ts = types[i]
    event_df = None
    if ds.endswith(".csv"):
        event_df = pd.read_csv(ds)
        print(event_df)
        for t in ts:
            event_df[t] = event_df[t].map(
                lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
        event_df["event_id"] = list(range(0, len(event_df)))
        event_df.index = list(range(0, len(event_df)))

    elif ds.endswith(".jsonocel"):
        event_df = import_factory.apply(ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
        for t in ts:
            event_df.loc[event_df[t].isnull(), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
    event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
    execution_extraction_parameters = [("weakly", "")] + [("leading", t) for t in ts]
    for technique, t in execution_extraction_parameters:

        s_time = time.time()
        print("TECHNIQUE: " + technique + " " + t)
        if t == "Entitlement application" or t == "Inspection":
            continue
        for isomporphism in ["complex", "naive"]:
            running_times[(ds, technique, t, isomporphism)] = []
            print(isomporphism)
            ocel = None
            if ind == 1:
                ocel = OCEL(event_df[:5000], ts, execution_extraction=technique, leading_object_type=t,
                        variant_extraction=isomporphism)
            else:
                ocel = OCEL(event_df[:50000], ts, execution_extraction=technique, leading_object_type=t,
                            variant_extraction=isomporphism)
            print("Number of cases: " + str(len(ocel.cases)))
            s_time = time.time()
            r_full_time = 0
            try:
                print("Number of equivalence classes: " + str(len(ocel.variants)))
                print("Took: " + str(time.time() - s_time))
                r_full_time = time.time() - s_time
            except Exception:
                print("Out of time")
                r_full_time = 0
            # Calculate time for both our isopmoprhism technique as well as the naive approach
            # maybe there are others form subgraphs?
            print("SUBRUNS")
            for j in range(1, 6):

                percentage_cases = (j / 10)
                sub_ocel = ocel.copy()
                sub_ocel.sample_cases(percentage_cases)
                num_cases = len(sub_ocel.cases)
                # case filtering needed
                # sub_ocel = execution_filtering.filter_cases(ocel,random.sample(ocel.cases,num_cases))
                sub_ocel.variant_timeout = 300
                print("Number of cases: " + str(len(sub_ocel.cases)))
                s_time = time.time()
                try:
                    print("Number of equivalence classes: " + str(len(sub_ocel.variants)))
                except Exception:
                    print("Out of time")
                    break
                    # running_times[(ds, technique, t, isomporphism)].append((num_cases, 0))
                r_time = time.time() - s_time
                running_times[(ds, technique, t, isomporphism)].append((num_cases, r_time))
            running_times[(ds, technique, t, isomporphism)].append((len(ocel.cases), r_full_time))
    # construct lines
    # color_map={"complex":"blue","naive":"red"}
    # #linestyle_map = {datasets[0]:"-",datasets[1]:"--"}#,datasets[2]:"-.",datasets[3]:":"}
    # symbols = [None,"o","v",".","^","<",">"]
    # for ds_ in datasets:
    #     plt.clf()
    #     for (ds,technique,t,isomorphism) in running_times.keys():
    #         if ds != ds_:
    #             continue
    #         ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
    #         pointer_map = {ext_params[i]:symbols[i] for i in range(0,len(ext_params))}
    #         x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
    #         y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
    #         plt.plot(x,y,color=color_map[isomorphism], marker=pointer_map[(technique,t)])
    #     plt.savefig("iso"+str(datasets.index(ds_))+".png")

    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22',
              '#17BECF']
    color_map = {"complex": colors[0], "naive": colors[1]}
    symbols = [None, "o", "v", ".", "^", "<", ">"]
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9, 5))
    ds_ = datasets[ind]
    for iso_technique in ["naive", "complex"]:
        x = []
        y = []
        # collect data
        for (ds, technique, t, isomorphism) in running_times.keys():
            if ds != ds_:
                continue
            if isomorphism != iso_technique:
                continue
            else:
                x += [elem[0] for elem in running_times[(ds, technique, t, isomorphism)]]
                y += [elem[1] for elem in running_times[(ds, technique, t, isomorphism)]]

        ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
        pointer_map = {ext_params[i]: symbols[i] for i in range(0, len(ext_params))}
        # x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
        # y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
        sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                        label="baseline" if iso_technique == "naive" else "two step approach")  # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
        # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Process Executions")
    plt.ylabel("Calculation Equivalence Classes in s")
    plt.title("Running Time for Computing Equivalence Classes, DS" + str(datasets.index(ds_) + 1))
    plt.tight_layout()

    plt.savefig("iso_sns_" + str(datasets.index(ds_) + 1) + ".png")
    return running_times

if x:
    random.seed(a=33)
    running_times = {}
    #Running times of extraction for different subsizes of each log and for different extraction techniques
    for i in range(0,len(datasets)):
        ds = datasets[i]
        print("_____________")
        print(ds)
        print("_____________")
        ts = types[i]
        event_df = None
        if ds.endswith(".csv"):
            event_df = pd.read_csv(ds)
            print(event_df)
            for t in ts:
                event_df[t] = event_df[t].map(
                    lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
            event_df["event_id"] = list(range(0, len(event_df)))
            event_df.index = list(range(0, len(event_df)))

        elif ds.endswith(".jsonocel"):
            event_df = import_factory.apply(ds,import_factory.OCEL_JSON, parameters={"return_df": True})[0]
            for t in ts:
                event_df.loc[event_df[t].isnull(),[t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
        event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
        execution_extraction_parameters = [("weakly","")] + [("leading",t) for t in ts]
        for technique, t in execution_extraction_parameters:

            s_time = time.time()
            print("TECHNIQUE: "+technique +" "+ t)
            if t == "Entitlement application" or t == "Inspection":
                continue
            for isomporphism in ["complex","naive"]:
                running_times[(ds, technique, t, isomporphism)] = []
                print(isomporphism)
                ocel = OCEL(event_df[:100000], ts, execution_extraction=technique,leading_object_type=t,variant_extraction=isomporphism)
                print("Number of cases: "+str(len(ocel.cases)))
                s_time = time.time()
                try:
                    print("Number of equivalence classes: "+str(len(ocel.variants)))
                    print("Took: " + str(time.time() - s_time))
                    r_full_time = time.time() - s_time
                except Exception:
                    print("Out of time")
                    r_full_time = 0
                #Calculate time for both our isopmoprhism technique as well as the naive approach
                #maybe there are others form subgraphs?
                print("SUBRUNS")
                for j in range(1,9):

                    percentage_cases = (j/10)
                    sub_ocel = ocel.copy()
                    sub_ocel.sample_cases(percentage_cases)
                    num_cases = len(sub_ocel.cases)
                    #case filtering needed
                    #sub_ocel = execution_filtering.filter_cases(ocel,random.sample(ocel.cases,num_cases))
                    sub_ocel.variant_timeout = 300
                    print("Number of cases: " + str(len(sub_ocel.cases)))
                    s_time = time.time()
                    try:
                        print("Number of equivalence classes: " + str(len(sub_ocel.variants)))
                    except Exception:
                        print("Out of time")
                        break
                        #running_times[(ds, technique, t, isomporphism)].append((num_cases, 0))
                    r_time = time.time() - s_time
                    running_times[(ds,technique,t,isomporphism)].append((num_cases,r_time))
                running_times[(ds, technique, t, isomporphism)].append((len(ocel.cases), r_full_time))
    #construct lines
    # color_map={"complex":"blue","naive":"red"}
    # #linestyle_map = {datasets[0]:"-",datasets[1]:"--"}#,datasets[2]:"-.",datasets[3]:":"}
    # symbols = [None,"o","v",".","^","<",">"]
    # for ds_ in datasets:
    #     plt.clf()
    #     for (ds,technique,t,isomorphism) in running_times.keys():
    #         if ds != ds_:
    #             continue
    #         ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
    #         pointer_map = {ext_params[i]:symbols[i] for i in range(0,len(ext_params))}
    #         x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
    #         y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
    #         plt.plot(x,y,color=color_map[isomorphism], marker=pointer_map[(technique,t)])
    #     plt.savefig("iso"+str(datasets.index(ds_))+".png")

    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
    color_map = {"complex": colors[0], "naive": colors[1]}
    symbols = [None, "o", "v", ".", "^", "<", ">"]
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9, 5))
    for ds_ in datasets:
        plt.clf()
        for iso_technique in ["naive","complex"]:
            x = []
            y = []
            #collect data
            for (ds,technique,t,isomorphism) in running_times.keys():
                if ds != ds_:
                    continue
                if isomorphism != iso_technique:
                    continue
                else:
                    x += [elem[0] for elem in running_times[(ds, technique, t, isomorphism)]]
                    y += [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]

            ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
            pointer_map = {ext_params[i]: symbols[i] for i in range(0, len(ext_params))}
            #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
            #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
            sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                         label="baseline" if iso_technique == "naive" else "two step approach")#) + ("leading type" +t) if t != "" else "weakly con. comp.")
            # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
        sns.despine()
        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Number of Process Executions")
        plt.ylabel("Calculation Equivalence Classes in s")
        plt.title("Running Time for Computing Equivalence Classes, DS"+str(datasets.index(ds_)+1))
        plt.tight_layout()

        plt.savefig("iso_sns_"+str(datasets.index(ds_)+1)+".png")


pool = ThreadPool(4)
result = pool.starmap(scalability_iso,zip([0,1,2,3],itertools.repeat(datasets),itertools.repeat(types)))
print(result)
running_times = {k: v for d in result for k, v in d.items()}
#Threadsafe plotting to ensure
colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
color_map = {"complex": colors[0], "naive": colors[1]}
symbols = [None, "o", "v", ".", "^", "<", ">"]
sns.set(rc={'figure.figsize': (24, 8)})
plt.rcParams["axes.labelsize"] = 16
plt.rcParams["axes.titlesize"] = 20

plt.figure(figsize=(9, 5))
for ds_ in datasets:
    plt.clf()
    for iso_technique in ["naive","complex"]:
        x = []
        y = []
        #collect data
        for (ds,technique,t,isomorphism) in running_times.keys():
            if ds != ds_:
                continue
            if isomorphism != iso_technique:
                continue
            else:
                x += [elem[0] for elem in running_times[(ds, technique, t, isomorphism)]]
                y += [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]

        ext_params = [("weakly", "")] + [("leading", t) for t in types[datasets.index(ds)]]
        pointer_map = {ext_params[i]: symbols[i] for i in range(0, len(ext_params))}
        #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
        #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
        sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                     label="baseline" if iso_technique == "naive" else "two step approach")#) + ("leading type" +t) if t != "" else "weakly con. comp.")
        # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Process Executions")
    plt.ylabel("Calculation Equivalence Classes in s")
    plt.title("Running Time for Computing Equivalence Classes, DS"+str(datasets.index(ds_)+1))
    plt.tight_layout()

    plt.savefig("iso_sns_final_"+str(datasets.index(ds_)+1)+".png")

#full graph of all

plt.clf()
for iso_technique in ["naive","complex"]:
    #collect data
    x = []
    y = []
    for (ds,technique,t,isomorphism) in running_times.keys():
        if isomorphism != iso_technique:
            continue
        else:
            x += [elem[0] for elem in running_times[(ds, technique, t, isomorphism)]]
            y += [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]


    pointer_map = {ext_params[i]: symbols[i] for i in range(0, len(ext_params))}
    #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
    #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
    sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                 label="baseline" if iso_technique == "naive" else "two step approach")#) + ("leading type" +t) if t != "" else "weakly con. comp.")
    # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
sns.despine()
plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
plt.xlabel("Number of Process Executions")
plt.ylabel("Calculation Equivalence Classes in s")
plt.title("Running Time for Computing Equivalence Classes")
plt.tight_layout()

plt.savefig("iso_sns_final.png")
######### Isomorphism times
#calculate number of variants for first and second step for all logs,

#calculate comparison numbers for number of classes and running tim efrom naive baseline
#for different subsets of cases, i.e., 10 percent, 20 percent etc.



######## Visualization
