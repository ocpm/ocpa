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
from ocpa.algo.feature_extraction import tabular, sequential
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import accuracy_score
from statistics import median as median
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
# TODO: Preprocessing and conversion from other types of OCEL


def avg(x):
    if len(x) == 0:
        return np.nan
    return sum(x)/len(x)

def std_dev(x):
    m = sum(x) / len(x)
    return sum((xi - m) ** 2 for xi in x) / len(x)

filename = "example_logs/mdl/BPI2017-Full-MDL.csv"
ots = ["application", "offer"]


event_df = pd.read_csv(filename, sep=',')[:50]
event_df["event_timestamp"] = pd.to_datetime(event_df["event_timestamp"])




print(event_df)
for ot in ots:
    event_df[ot] = event_df[ot].map(
        lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
event_df["event_id"] = list(range(0, len(event_df)))
event_df.index = list(range(0, len(event_df)))
event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
event_df["event_start_timestamp"] = pd.to_datetime(event_df["event_start_timestamp"])
#####FAKE FEATURE VALUE
event_df["event_fake_feat"] = 1
event_df.drop(columns = "Unnamed: 0", inplace=True)
ocel = OCEL(event_df, ots)
t_start = time.time()
print("Number of process executions: "+str(len(ocel.cases)))
print(str(time.time()-t_start))
print(ocel.log)
#ALL FEATURES
#F = [(feature_extraction.EVENT_NUM_OF_OBJECTS,()),(feature_extraction.EVENT_TYPE_COUNT,("offer",)),(feature_extraction.EVENT_PRECEDING_ACTIVITES,("Create application",)),(feature_extraction.EVENT_PREVIOUS_ACTIVITY_COUNT,("Create application",)),(feature_extraction.EVENT_CURRENT_ACTIVITIES,("Create application",)),(feature_extraction.EVENT_AGG_PREVIOUS_CHAR_VALUES,("fake_feat",sum)),(feature_extraction.EVENT_PRECEDING_CHAR_VALUES,("fake_feat",sum)),(feature_extraction.EVENT_CHAR_VALUE,("fake_feat",)),(feature_extraction.EVENT_CURRENT_RESOURCE_WORKLOAD,("fake_feat",timedelta(days=1))),(feature_extraction.EVENT_CURRENT_TOTAL_WORKLOAD,("fake_feat",timedelta(days=1))),(feature_extraction.EVENT_RESOURCE,("fake_feat",1)),(feature_extraction.EVENT_CURRENT_TOTAL_OBJECT_COUNT,(timedelta(days=1),)),(feature_extraction.EVENT_PREVIOUS_OBJECT_COUNT,()),(feature_extraction.EVENT_PREVIOUS_TYPE_COUNT,("offer",)),(feature_extraction.EVENT_OBJECTS,(('application', "{'Application_1966208034'}"),)),(feature_extraction.EVENT_EXECUTION_DURATION,()),(feature_extraction.EVENT_ELAPSED_TIME,()),(feature_extraction.EVENT_REMAINING_TIME,()),(feature_extraction.EVENT_FLOW_TIME,(ocpn,)),(feature_extraction.EVENT_SYNCHRONIZATION_TIME,(ocpn,)),(feature_extraction.EVENT_POOLING_TIME,(ocpn,"offer")),(feature_extraction.EVENT_WAITING_TIME,(ocpn,"event_start_timestamp"))]
#ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
if False:
    #F = [(feature_extraction.EVENT_NUM_OF_OBJECTS,()),(feature_extraction.EVENT_TYPE_COUNT,("offer",)),(feature_extraction.EVENT_PRECEDING_ACTIVITES,("Create application",)),(feature_extraction.EVENT_PREVIOUS_OBJECT_COUNT,()),(feature_extraction.EVENT_PREVIOUS_TYPE_COUNT,("offer",)),(feature_extraction.EVENT_ELAPSED_TIME,()),(feature_extraction.EVENT_REMAINING_TIME,())]
    F = [(feature_extraction.EVENT_FLOW_TIME,(ocpn,)),(feature_extraction.EVENT_SYNCHRONIZATION_TIME,(ocpn,)),(feature_extraction.EVENT_POOLING_TIME,(ocpn,"offer")),(feature_extraction.EVENT_WAITING_TIME,(ocpn,"event_start_timestamp"))]

    feature_storage = feature_extraction.apply(ocel,F,[])
    table = tabular.construct_table(feature_storage)
    print(table)
    #sequences = sequential.construct_sequence(feature_storage)


#CASE STUDY 1 - VISUALIZING TABLE
if False:
    feat_to_s = {}
    f_in = ocpa.algo.filtering.log.time_filtering.events
    s_time= time.time()
    s, time_index = time_series.construct_time_series(ocel, timedelta(days=7),
                                                      [(avg, (feature_extraction.EVENT_TYPE_COUNT,("offer",))),
                                                       (avg, (feature_extraction.EVENT_CHAR_VALUE,("event_RequestedAmount",)))],
                                                      [],
                                                      f_in)
    print("total time series: " + str(time.time() - s_time))
    for feat in s.keys():
        if feat not in feat_to_s.keys():
            feat_to_s[feat] = []
        feat_to_s[feat].append((s[feat], time_index))
    print(feat_to_s)
    data_df = pd.DataFrame({"date":feat_to_s[list(feat_to_s.keys())[0]][0][1]})
    for feat in feat_to_s.keys():
        name = ""
        if feat == list(feat_to_s.keys())[0]:
            name = "Average Number of Objects"
        else:
            name = "Average Remaining Time in s"
        data_df[name] = [feat_to_s[feat][0][0][i] for i in range(0,len(feat_to_s[feat][0][0]))]
    plt.clf()
    plt.rcParams["axes.labelsize"] = 20
    plt.rcParams["axes.titlesize"] = 28
    plt.figure(figsize=(10, 5))
    sns.set(rc={'figure.figsize': (30, 8)})
    data_df.set_index('date', inplace=True)
    sns.set_style("darkgrid")
    plot_ = sns.lineplot(data=data_df["Average Number of Objects"], color = "#4C72B0")
    ax2 = plt.twinx()
    sns.lineplot(data=data_df["Average Remaining Time in s"], ax = ax2, color="#DD8452")
    for index, label in enumerate(plot_.get_xticklabels()):
        if index % 2 == 0:
            label.set_visible(True)
        else:
            label.set_visible(False)
    #plot_.legend()
    plot_.set_title("Time Series")
    plot_.set_ylabel("Average Number of Offer Objects", color = "#4C72B0")
    ax2.set_ylabel("Average Requested Amount", color="#DD8452")
    plot_.set_xlabel(
        "Date")
    plt.savefig("CS_time_series.png",dpi=600)

##Case Study 2 - Regression
if False:
    activities = list(set(ocel.log["event_activity"].tolist()))
    F = [(feature_extraction.EVENT_REMAINING_TIME,()),(feature_extraction.EVENT_PREVIOUS_TYPE_COUNT,("offer",)),(feature_extraction.EVENT_ELAPSED_TIME,())] + [(feature_extraction.EVENT_ACTIVITY,(act,)) for act in activities] + [(feature_extraction.EVENT_PREVIOUS_ACTIVITY_COUNT,(act,)) for act in activities]
    feature_storage = feature_extraction.apply(ocel, F, [])
    table = tabular.construct_table(feature_storage)
    y = table[F[0]]
    x = table.drop(F[0], axis = 1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=4715)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    print('MAE: ', mean_absolute_error(y_test, y_pred)/3600/24)
    test = pd.DataFrame({'Predicted value': y_pred, 'Actual value': y_test})
    fig = plt.figure(figsize=(16, 8))
    test = test.reset_index()
    test = test.drop(['index'], axis=1)
    plt.plot(test[:100])
    plt.legend(['Actual value', 'Predicted value'])
    plt.savefig("prediction_reg.png",dpi=600)

#CASE Study 3 - Visualizing Sequence
if False:
    activities = list(set(ocel.log["event_activity"].tolist()))
    F = [(feature_extraction.EVENT_ACTIVITY,(act,)) for act in activities]
    feature_storage = feature_extraction.apply(ocel,F,[])
    sequences = sequential.construct_sequence(feature_storage)

    print(sequences[0])

#CASE Study 4 - Prediction - LSTM
if True:
    k=4
    activities = list(set(ocel.log["event_activity"].tolist()))
    F = [(feature_extraction.EVENT_REMAINING_TIME,())]+[(feature_extraction.EVENT_ACTIVITY, (act,)) for act in activities]
    feature_storage = feature_extraction.apply(ocel, F, [])
    features = [feat for feat in feature_storage.event_features if feat != (feature_extraction.EVENT_REMAINING_TIME,())]
    target = (feature_extraction.EVENT_REMAINING_TIME,())
    sequences = sequential.construct_sequence(feature_storage)
    X = []
    y = []
    for s in sequences:
        if len(s) != 0:
            for i in range(k-1,len(s)):
                seq = []
                for j in range(i-(k-1),i+1):
                    seq.append([s[j][feat] for feat in features])
                y.append(s[i][target])
                X.append(seq)
    print(X)
    print(y)