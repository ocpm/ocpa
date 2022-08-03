import pandas as pd
from ast import literal_eval

import ocpa.algo.util.process_executions.factory
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.importer.mdl import factory as ocel_import_factory
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.algo.evaluation.precision_and_fitness import evaluator as quality_measure_factory

filename = "example_logs/mdl/BPI2017-Final.csv"
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
ocel = ocel_import_factory.apply(file_path= filename,parameters = {"obj_names":ots,"val_names":[],"act_name":"event_activity","time_name":"event_timestamp","sep":",","execution_extraction":ocpa.algo.util.process_executions.factory.CONN_COMP,"leading_type":ots[0],"variant_calculation":ocpa.algo.util.variants.factory.ONE_PHASE})
#print(len(ocel.process_executions))
#print(len(ocel.variants))
ocpn = ocpn_discovery_factory.apply(ocel)
precision, fitness = quality_measure_factory.apply(ocel, ocpn)
print(precision)
print(fitness)