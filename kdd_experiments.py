import itertools
import random
import time

from ocpa.objects.log.ocel import OCEL
import pandas as pd
import ocpa.objects.log.importer.ocel.factory as import_factory
import ocpa.visualization.log.variants.factory as log_viz
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
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


# Datasets
datasets = ["example_logs/mdl/BPI2017.csv", "example_logs/jsonxml/running-example.jsonocel",
            "example_logs/mdl/incident.csv", "example_logs/mdl/BPI_2018_2017.csv"]
###datasets = ["example_logs/mdl/Full_slim_minimal.csv","example_logs/mdl/BPI_2018_2017.csv"]
# Here are som eproblems with respect to purchase as leading object type, the first 10 percent of th elog does not contain any purchase, i.e., producing division by zero error
#datasets = ["example_logs/mdl/BPI2019.csv"]
types = [["application", "offer"], ["items", "orders", "packages"], ["incident", "customer"], ["Payment application",
                                                                                               "Control summary", "Entitlement application", "Geo parcel document", "Inspection", "Reference alignment"]]
###types = [["application", "offer"],["Payment application","Control summary","Entitlement application","Geo parcel document","Inspection","Reference alignment"]]
#types = [["Purchase","Item"]]

# Extraction running times
# Basic statistics for the five event data sets
x = False
if False:
    running_times = {}
    for i in [0, 2]:  # range(0,len(datasets)):
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
            event_df = import_factory.apply(
                ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
            for t in ts:
                event_df.loc[event_df[t].isnull(
                ), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
        event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
        execution_extraction_parameters = [
            ("weakly", "")] + [("leading", t) for t in ts]
        for technique, t in execution_extraction_parameters:
            s_time = time.time()
            print(technique + " " + t)
            ocel = OCEL(event_df, ts, execution_extraction=technique,
                        leading_object_type=t)
            print("Number of cases: " + str(len(ocel.process_executions)))
            r_full_time = time.time() - s_time
            sum_lengths = 0
            max_length = 0
            min_length = 10000000
            sum_obs = 0
            max_obs = 0
            min_obs = 10000000
            for i in range(0, len(ocel.process_executions)):
                exec = ocel.process_executions[i]
                num_events = len(exec)
                if num_events > max_length:
                    max_length = num_events
                if min_length > num_events:
                    min_length = num_events
                sum_lengths += num_events
                case_obs = ocel.process_execution_objects[i]
                num_obs = len(case_obs)
                if num_obs > max_obs:
                    max_obs = num_obs
                if min_obs > num_obs:
                    min_obs = num_obs
                sum_obs += num_obs
            avg_length = sum_lengths/len(ocel.process_executions)
            avg_obs = sum_obs / len(ocel.process_executions)
            print("Max length: "+str(max_length))
            print("Min length: " + str(min_length))
            print("Avg length: " + str(avg_length))
            print("Max objects: " + str(max_obs))
            print("Min objects: " + str(min_obs))
            print("Avg objects: " + str(avg_obs))
            print("Took: "+str(time.time()-s_time))
            # get execution times
            print(technique + " " + t)
            running_times[(ds, technique, t)] = []
            continue
            for t_dev in range(1, 10):
                log_size = int(len(event_df)/10*t_dev)
                print("___________")
                print("For size" + str(log_size))
                s_time = time.time()
                ocel = OCEL(
                    event_df[:log_size], ts, execution_extraction=technique, leading_object_type=t)
                print("Number of cases: " + str(len(ocel.process_executions)))
                print("Took: " + str(time.time() - s_time))
                r_time = time.time() - s_time
                running_times[(ds, technique, t)].append((log_size, r_time))
                #print("Number of cases: " + str(len(ocel.cases)))
            running_times[(ds, technique, t)].append((len(event_df), r_time))
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
              '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
    color_map = {datasets[0]: colors[0], datasets[1]: colors[1],
                 datasets[2]: colors[2], datasets[3]: colors[3]}
    symbols = [None, "o", "v", ".", "^", "<", ">"]
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9, 5))
    for ds_ in datasets:
        # plt.clf()
        for (ds, technique, t) in running_times.keys():
            if ds != ds_:
                continue
            ext_params = [("weakly", "")] + [("leading", t)
                                             for t in types[datasets.index(ds)]]
            pointer_map = {ext_params[i]: symbols[i]
                           for i in range(0, len(ext_params))}
            x = [elem[0] for elem in running_times[(ds, technique, t)]]
            y = [elem[1] for elem in running_times[(ds, technique, t)]]
            sns.lineplot(x, y, color=color_map[ds_], marker=pointer_map[(
                technique, t)], label="DS"+str(datasets.index(ds_)+1)+" "+t)
            #plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Events")
    plt.ylabel("Running Time of Extraction in s")
    plt.title("Running Time of Execution Extraction")
    plt.tight_layout()

    plt.savefig("__extr_sns_full"+".png")

print("______________")
print("______________")
print("Isomorphism comparison")
print("______________")
print("______________")


def results_two_steps_iso(ind, datasets, types):
    random.seed(a=33)
    results = {}
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
        event_df = import_factory.apply(
            ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
        for t in ts:
            event_df.loc[event_df[t].isnull(
            ), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
    event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
    execution_extraction_parameters = [
        ("weakly", "")] + [("leading", t) for t in ts]
    for technique, t in execution_extraction_parameters:
        s_time = time.time()
        print("TECHNIQUE: " + technique + " " + t)
        ocel = None
        if ind == 1:
            ocel = OCEL(event_df, ts, execution_extraction=technique, leading_object_type=t,
                        variant_extraction="complex")

        else:
            ocel = OCEL(event_df, ts, execution_extraction=technique, leading_object_type=t,
                        variant_extraction="complex")
        print("Number of cases: " + str(len(ocel.process_executions)))
        ocel.variant_timeout = 22000
        s_time = time.time()
        r_full_time = 0
        n_before, n_after, t_first, t_second = ocel.calculate_variants_with_data()
        print("FOR "+str(ind)+" WITH TECHNIQUE "+technique+" " +
              t+" NUMBER OF EQUIVALENCE CLASSES: " + str(n_after))
        results[(ds, technique, t)] = (n_before, n_after, t_first, t_second)
    return results


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
        event_df = import_factory.apply(
            ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
        for t in ts:
            event_df.loc[event_df[t].isnull(
            ), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
    event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
    execution_extraction_parameters = [
        ("weakly", "")] + [("leading", t) for t in ts]
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
            print("Number of cases: " + str(len(ocel.process_executions)))
            s_time = time.time()
            r_full_time = 0
            try:
                print("Number of equivalence classes: " +
                      str(len(ocel.variants)))
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
                num_cases = len(sub_ocel.process_executions)
                # case filtering needed
                # sub_ocel = execution_filtering.filter_cases(ocel,random.sample(ocel.cases,num_cases))
                sub_ocel.variant_timeout = 300
                print("Number of cases: " + str(len(sub_ocel.process_executions)))
                s_time = time.time()
                try:
                    print("Number of equivalence classes: " +
                          str(len(sub_ocel.variants)))
                except Exception:
                    print("Out of time")
                    break
                    # running_times[(ds, technique, t, isomporphism)].append((num_cases, 0))
                r_time = time.time() - s_time
                running_times[(ds, technique, t, isomporphism)
                              ].append((num_cases, r_time))
            running_times[(ds, technique, t, isomporphism)].append(
                (len(ocel.process_executions), r_full_time))
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
                x += [elem[0]
                      for elem in running_times[(ds, technique, t, isomorphism)]]
                y += [elem[1]
                      for elem in running_times[(ds, technique, t, isomorphism)]]

        ext_params = [("weakly", "")] + [("leading", t)
                                         for t in types[datasets.index(ds)]]
        pointer_map = {ext_params[i]: symbols[i]
                       for i in range(0, len(ext_params))}
        # x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
        # y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
        sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                        label="baseline" if iso_technique == "naive" else "two step approach")  # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
        # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Process Executions")
    plt.ylabel("Calculation Equivalence Classes in s")
    plt.title("Running Time for Computing Equivalence Classes, DS" +
              str(datasets.index(ds_) + 1))
    plt.tight_layout()

    plt.savefig("iso_sns_" + str(datasets.index(ds_) + 1) + ".png")
    return running_times


if False:
    random.seed(a=33)
    running_times = {}
    # Running times of extraction for different subsizes of each log and for different extraction techniques
    for i in range(0, len(datasets)):
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
            event_df = import_factory.apply(
                ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
            for t in ts:
                event_df.loc[event_df[t].isnull(
                ), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
        event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
        execution_extraction_parameters = [
            ("weakly", "")] + [("leading", t) for t in ts]
        for technique, t in execution_extraction_parameters:

            s_time = time.time()
            print("TECHNIQUE: "+technique + " " + t)
            if t == "Entitlement application" or t == "Inspection":
                continue
            for isomporphism in ["complex", "naive"]:
                running_times[(ds, technique, t, isomporphism)] = []
                print(isomporphism)
                ocel = OCEL(event_df[:100000], ts, execution_extraction=technique,
                            leading_object_type=t, variant_extraction=isomporphism)
                print("Number of cases: " + str(len(ocel.process_executions)))
                s_time = time.time()
                try:
                    print("Number of equivalence classes: " +
                          str(len(ocel.variants)))
                    print("Took: " + str(time.time() - s_time))
                    r_full_time = time.time() - s_time
                except Exception:
                    print("Out of time")
                    r_full_time = 0
                # Calculate time for both our isopmoprhism technique as well as the naive approach
                # maybe there are others form subgraphs?
                print("SUBRUNS")
                for j in range(1, 9):

                    percentage_cases = (j/10)
                    sub_ocel = ocel.copy()
                    sub_ocel.sample_cases(percentage_cases)
                    num_cases = len(sub_ocel.process_executions)
                    # case filtering needed
                    #sub_ocel = execution_filtering.filter_cases(ocel,random.sample(ocel.cases,num_cases))
                    sub_ocel.variant_timeout = 300
                    print("Number of cases: " + str(len(sub_ocel.process_executions)))
                    s_time = time.time()
                    try:
                        print("Number of equivalence classes: " +
                              str(len(sub_ocel.variants)))
                    except Exception:
                        print("Out of time")
                        break
                        #running_times[(ds, technique, t, isomporphism)].append((num_cases, 0))
                    r_time = time.time() - s_time
                    running_times[(ds, technique, t, isomporphism)
                                  ].append((num_cases, r_time))
                running_times[(ds, technique, t, isomporphism)].append(
                    (len(ocel.process_executions), r_full_time))
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

    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
              '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
    color_map = {"complex": colors[0], "naive": colors[1]}
    symbols = [None, "o", "v", ".", "^", "<", ">"]
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9, 5))
    for ds_ in datasets:
        plt.clf()
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
                    x += [elem[0]
                          for elem in running_times[(ds, technique, t, isomorphism)]]
                    y += [elem[1]
                          for elem in running_times[(ds, technique, t, isomorphism)]]

            ext_params = [("weakly", "")] + [("leading", t)
                                             for t in types[datasets.index(ds)]]
            pointer_map = {ext_params[i]: symbols[i]
                           for i in range(0, len(ext_params))}
            #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
            #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
            sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                            label="baseline" if iso_technique == "naive" else "two step approach")  # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
            # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
        sns.despine()
        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Number of Process Executions")
        plt.ylabel("Calculation Equivalence Classes in s")
        plt.title("Running Time for Computing Equivalence Classes, DS" +
                  str(datasets.index(ds_)+1))
        plt.tight_layout()

        plt.savefig("iso_sns_"+str(datasets.index(ds_)+1)+".png")

if False:
    pool = ThreadPool(4)
    result = pool.starmap(scalability_iso, zip(
        [0, 1, 2, 3], itertools.repeat(datasets), itertools.repeat(types)))
    print(result)
    running_times = {k: v for d in result for k, v in d.items()}
    # Threadsafe plotting to ensure
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
              '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22', '#17BECF']
    color_map = {"complex": colors[0], "naive": colors[1]}
    symbols = [None, "o", "v", ".", "^", "<", ">"]
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(9, 5))
    for ds_ in datasets:
        plt.clf()
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
                    x += [elem[0]
                          for elem in running_times[(ds, technique, t, isomorphism)]]
                    y += [elem[1]
                          for elem in running_times[(ds, technique, t, isomorphism)]]

            ext_params = [("weakly", "")] + [("leading", t)
                                             for t in types[datasets.index(ds)]]
            pointer_map = {ext_params[i]: symbols[i]
                           for i in range(0, len(ext_params))}
            #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
            #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
            sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                            label="baseline" if iso_technique == "naive" else "two step approach")  # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
            # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
        sns.despine()
        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
        plt.xlabel("Number of Process Executions")
        plt.ylabel("Calculation Equivalence Classes in s")
        plt.title("Running Time for Computing Equivalence Classes, DS" +
                  str(datasets.index(ds_)+1))
        plt.tight_layout()

        plt.savefig("iso_sns_final_"+str(datasets.index(ds_)+1)+".png")


# ISOMORPHISM RUNNING TIMES

    plt.clf()
    for iso_technique in ["naive", "complex"]:
        # collect data
        x = []
        y = []
        for (ds, technique, t, isomorphism) in running_times.keys():
            if isomorphism != iso_technique:
                continue
            else:
                x += [elem[0]
                      for elem in running_times[(ds, technique, t, isomorphism)]]
                y += [elem[1]
                      for elem in running_times[(ds, technique, t, isomorphism)]]

        pointer_map = {ext_params[i]: symbols[i]
                       for i in range(0, len(ext_params))}
        #x = [elem[0] for elem in running_times[(ds,technique,t,isomorphism)]]
        #y = [elem[1] for elem in running_times[(ds,technique,t,isomorphism)]]
        sns.scatterplot(x, y, color=color_map[iso_technique], marker="o",
                        label="baseline" if iso_technique == "naive" else "two step approach")  # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
        # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    plt.xlabel("Number of Process Executions")
    plt.ylabel("Calculation Equivalence Classes in s")
    plt.title("Running Time for Computing Equivalence Classes")
    plt.tight_layout()

    plt.savefig("iso_sns_final.png")

# Dissassmebled runnign times isomorphism
if True:
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22',
              '#17BECF']
    results_df = []
    pool = ThreadPool(4)
    result = pool.starmap(results_two_steps_iso, zip(
        [0, 1, 2, 3], itertools.repeat(datasets), itertools.repeat(types)))
    print(result)
    results = {k: v for d in result for k, v in d.items()}
    for ds in datasets:
        ds_counter = 0
        for (ds_, technique, t) in results.keys():
            if ds_ != ds:
                continue
            ds_counter += 1
            ds_ind = datasets.index(ds)+1
            results_df.append({'dataset': "DS"+str(ds_ind),
                               'dataset_x': "DS" + str(ds_ind)+"_"+technique+" "+t,
                               'hue': str(ds_counter),
                               'technique': technique+t,
                               'first_step': results[(ds_, technique, t)][2]/(results[(ds_, technique, t)][2]+results[(ds_, technique, t)][3]),
                               # results[(ds_,technique,t)][3]/(results[(ds_,technique,t)][2]+results[(ds_,technique,t)][3]),
                               'second_step': 1,
                               'first_by_second': results[(ds_, technique, t)][0]/results[(ds_, technique, t)][1]})
    results_df = pd.DataFrame(results_df)
    print(results_df)
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20

    plt.figure(figsize=(10, 5))

    palette = {"1": colors[1], "2": colors[1], "3": colors[1],
               "4": colors[1], "5": colors[1], "6": colors[1], "7": colors[1]}
    bar1 = sns.barplot(x="dataset", y="second_step", hue="hue",
                       data=results_df, color=colors[1],  palette=palette)
    palette = {"1": colors[0], "2": colors[0], "3": colors[0], "4": colors[0], "5": colors[0], "6": colors[0],
               "7": colors[0]}
    bar2 = sns.barplot(x="dataset", y="first_step", hue="hue",
                       data=results_df, color=colors[0],  palette=palette)
    top_bar = mpatches.Patch(color=colors[1], label='Second Step')
    bottom_bar = mpatches.Patch(color=colors[0], label='First Step')
    plt.legend(handles=[top_bar, bottom_bar])
    plt.legend(bbox_to_anchor=(.01, 1), loc=2, borderaxespad=0.)
    plt.legend(handles=[top_bar, bottom_bar], loc='lower right')
    plt.xlabel("Data Sets and Different Extraction Techniques")
    plt.ylabel("Relative Share of Computation Time")
    plt.title("Distribution of Running Time Between The Two Steps")
    plt.ylim(0, 1.03)
    ax2 = plt.twinx()
    print(bar2.get_xticks())

    x_ticks = []
    width = 0.1111
    for t in range(-3, 0):
        x_ticks.append(0+t*width)
    for t in range(-3, 1):
        x_ticks.append(1+t*width)
    for t in range(-3, 0):
        x_ticks.append(2+t*width)
    for t in range(-3, 4):
        x_ticks.append(3+t*width)
    sns.lineplot(x_ticks, results_df['first_by_second'],
                 color=colors[7], marker="o", ax=ax2)
    ax2.set_ylabel(
        '#Initial Classes divided by #Refined Classes', color=colors[7])
    ax2.set(ylim=(0, 1.03))
    ax2.grid(False)
    sns.despine()
    plt.tight_layout()
    #sns.catplot(x="dataset",y="first_step",hue="technique", kind="bar", data=results_df)
    plt.savefig("first_second_new_.png")


# calculate comparison numbers for number of classes and running tim efrom naive baseline
# for different subsets of cases, i.e., 10 percent, 20 percent etc.


# Visualization
def results_variant_layouting(ind, datasets, types):
    random.seed(a=33)
    results = []
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
        event_df = import_factory.apply(
            ds, import_factory.OCEL_JSON, parameters={"return_df": True})[0]
        for t in ts:
            event_df.loc[event_df[t].isnull(
            ), [t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
    event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
    # + [("leading", t) for t in ts]
    execution_extraction_parameters = [("weakly", "")]
    # if ind == 1 or ind == 2:
    #    execution_extraction_parameters += [("leading", t) for t in ts[1:]]
    for technique, t in execution_extraction_parameters:
        s_time = time.time()
        print("TECHNIQUE: " + technique + " " + t)
        ocel = None
        if ind == 1:
            ocel = OCEL(event_df, ts, execution_extraction=technique, leading_object_type=t,
                        variant_extraction="complex")
        else:
            ocel = OCEL(event_df, ts, execution_extraction=technique, leading_object_type=t,
                        variant_extraction="complex")
        print("Number of cases: " + str(len(ocel.process_executions)))
        print("Number of variants: " + str(len(ocel.variants)))
        print(str(ind) + "start")
        results += log_viz.apply(ocel, parameters={"measure": True})
        print(str(ind) + "done")
    return results


if False:
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#CFECF9', '#7F7F7F', '#BCBD22',
              '#17BECF']
    pool = ThreadPool(4)
    result = pool.starmap(results_variant_layouting, zip(
        [0, 1, 2, 3], itertools.repeat(datasets), itertools.repeat(types)))
    print(result)
    results = []  # {k: v for d in result for k, v in d.items()}
    for r in result:
        results += r
    plt.clf()
    sns.set(rc={'figure.figsize': (24, 8)})
    plt.rcParams["axes.labelsize"] = 16
    plt.rcParams["axes.titlesize"] = 20
    cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)
    plt.figure(figsize=(10, 5))
    # collect data
    x = [elem[0] for elem in results]
    x2 = [elem[1] for elem in results]
    y = [elem[2] for elem in results]
    # ) + ("leading type" +t) if t != "" else "weakly con. comp.")
    sns.scatterplot(x, y, color=colors[0],
                    marker="o", size=x2, palette=cmap, hue=x2)
    # plt.plot(x,y,color=color_map[ds_], marker=pointer_map[(technique,t)])
    sns.despine()
    plt.legend(
        title='Number of Objects')
    plt.xlabel("Number of Events")
    plt.ylabel("Layouting Time in s")
    plt.title("Layout Calculation Time")
    plt.tight_layout()

    plt.savefig("v_run_.png")


# index_ = 1
# ds = datasets[index_]
# lt = types[index_][0]
# print("_____________")
# print(ds)
# print("_____________")
# ts = types[index_]
# event_df = None
# if ds.endswith(".csv"):
#     event_df = pd.read_csv(ds)
#     print(event_df)
#     for t in ts:
#         event_df[t] = event_df[t].map(
#             lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
#     event_df["event_id"] = list(range(0, len(event_df)))
#     event_df.index = list(range(0, len(event_df)))
#
# elif ds.endswith(".jsonocel"):
#     event_df = import_factory.apply(ds,import_factory.OCEL_JSON, parameters={"return_df": True})[0]
#     for t in ts:
#         event_df.loc[event_df[t].isnull(),[t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
# event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# ocel = OCEL(event_df[:1000], ts, execution_extraction="leading", leading_object_type=lt,
#                     variant_extraction="complex")
# print(len(ocel.cases))
# print(len(ocel.variants))
#
# ds = datasets[index_]
# print("_____________")
# print(ds)
# print("_____________")
# ts = types[index_]
# event_df = None
# if ds.endswith(".csv"):
#     event_df = pd.read_csv(ds)
#     print(event_df)
#     for t in ts:
#         event_df[t] = event_df[t].map(
#             lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
#     event_df["event_id"] = list(range(0, len(event_df)))
#     event_df.index = list(range(0, len(event_df)))
#
# elif ds.endswith(".jsonocel"):
#     event_df = import_factory.apply(ds,import_factory.OCEL_JSON, parameters={"return_df": True})[0]
#     for t in ts:
#         event_df.loc[event_df[t].isnull(),[t]] = event_df.loc[event_df[t].isnull(), t].apply(lambda x: [])
# event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# ocel = OCEL(event_df[:1000], ts, execution_extraction="leading", leading_object_type=lt,
#                     variant_extraction="naive")
# print(len(ocel.variants))
