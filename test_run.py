import pandas as pd

import ocpa.algo.util.process_executions.factory
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
import ocpa.algo.feature_extraction.factory as feature_extraction
from ocpa.algo.feature_extraction import tabular
from sklearn.linear_model import LinearRegression
from sklearn.metrics import  mean_absolute_error

filename = "sample_logs/csv/BPI2017-Final.csv"
ots = ["application", "offer"]
event_df = pd.read_csv(filename, sep=',')[:2000]
event_df["event_timestamp"] = pd.to_datetime(event_df["event_timestamp"])
event_df = event_df.sort_values(by='event_timestamp')

# def eval(x):
#     try:
#         return literal_eval(x.replace('set()', '{}'))
#     except:
#         return []
#
#
# print(event_df)
# for ot in ots:
#     # Option 1
#     event_df[ot] = event_df[ot].apply(eval)
#     # Option 2
#     # event_df[ot] = event_df[ot].map(
#     #    lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
# event_df["event_id"] = list(range(0, len(event_df)))
# event_df.index = list(range(0, len(event_df)))
# event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
# event_df["event_start_timestamp"] = pd.to_datetime(
#     event_df["event_start_timestamp"])
# # FAKE FEATURE VALUE
# event_df["event_fake_feat"] = 1
#event_df.drop(columns = "Unnamed: 0", inplace=True)
#event_df.drop(columns = "Unnamed: 1", inplace=True)
ocel = ocel_import_factory.apply(file_path= filename,parameters = {"obj_names":ots,"val_names":[],"act_name":"event_activity","time_name":"event_timestamp","sep":",","execution_extraction":ocpa.algo.util.process_executions.factory.CONN_COMP,"leading_type":ots[0],"variant_calculation":ocpa.algo.util.variants.factory.TWO_PHASE})
print("Number of cases"+str(len(ocel.process_executions)))
print("Number of variants"+str(len(ocel.variants)))
#ocpn = ocpn_discovery_factory.apply(ocel, parameters = {"debug":False})
#precision, fitness = quality_measure_factory.apply(ocel, ocpn)
#print("Precision of IM-discovered net: "+str(precision))
#print("Fitness of IM-discovered net: "+str(fitness))


print("Feature Extraction and Prediction Example")
activities = list(set(ocel.log.log["event_activity"].tolist()))
F = [(feature_extraction.EVENT_REMAINING_TIME, ()),
     (feature_extraction.EVENT_PREVIOUS_TYPE_COUNT, ("offer",)),
     (feature_extraction.EVENT_ELAPSED_TIME, ())] + [(feature_extraction.EVENT_AGG_PREVIOUS_CHAR_VALUES, ("event_RequestedAmount", max))] \
    + [(feature_extraction.EVENT_PRECEDING_ACTIVITES, (act,))
        for act in activities]
feature_storage = feature_extraction.apply(ocel, F, [])
feature_storage.extract_normalized_train_test_split(0.3, state = 3395)
train_table = tabular.construct_table(
        feature_storage, index_list=feature_storage.training_indices)
test_table = tabular.construct_table(
        feature_storage, index_list=feature_storage.test_indices)
y_train, y_test = train_table[F[0]], test_table[F[0]]
x_train, x_test = train_table.drop(
        F[0], axis=1), test_table.drop(F[0], axis=1)
model = LinearRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
avg_rem = sum(y_train)/len(y_train)
print('MAE baseline: ', mean_absolute_error(
    y_test, [avg_rem for elem in y_test]))
print('MAE: ', mean_absolute_error(y_test, y_pred))