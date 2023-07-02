# from sklearn.linear_model import LinearRegression
from ocpa.util.util import LinearRegression
# from sklearn.metrics import mean_absolute_error
from ocpa.util.util import mean_absolute_error
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
from ocpa.algo.predictive_monitoring import tabular
from ocpa.util.util import StandardScaler

import numpy as np

# def test_process_execution_extraction():
#     filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
#     ocel = ocel_import_factory.apply(filename)
#     activities = list(set(ocel.log.log["event_activity"].tolist()))
#     feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
#                    (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
#                    (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
#                   [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,))
#                    for act in activities]
#     feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
#     feature_storage.extract_normalized_train_test_split(0.3, state=3395)
#     train_table = tabular.construct_table(
#         feature_storage, index_list=feature_storage.training_indices)
#     test_table = tabular.construct_table(
#         feature_storage, index_list=feature_storage.test_indices)
#     y_train, y_test = train_table[feature_set[0]], test_table[feature_set[0]]
#     x_train, x_test = train_table.drop(
#         feature_set[0], axis=1), test_table.drop(feature_set[0], axis=1)
#     model = LinearRegression()
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     avg_rem = sum(y_train) / len(y_train)
#     MAE_base = mean_absolute_error(
#         y_test, [avg_rem for elem in y_test])
#     MAE = mean_absolute_error(y_test, y_pred)
#     assert 0.899 < MAE_base < 0.9
#     assert 0.06 < MAE < 0.07
