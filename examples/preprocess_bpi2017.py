import math
import pandas as pd
from ocpa.objects.ocel.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator

filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full.csv"
df = pd.read_csv(filename)

# sampling
sampling = True
if sampling == True:
    applications = set(df["case"])
    num_apps = len(applications)
    sample_size = int(num_apps*0.01)
    samples = list(applications)[:sample_size]
    sample_df = df.loc[df["case"].isin(samples)]
    sample_df.reset_index(inplace=True)

else:
    sample_df = df
    sample_df.reset_index(inplace=True)

# renaming column names
sample_df = sample_df.rename(columns={"index": "event_id", "case": "ApplicationID", "event": "event_activity",
                                      "completeTime": "event_timestamp", "startTime": "event_start_timestamp"})
# filtering relevant columns
sample_df = sample_df[["event_id", "event_activity", "event_timestamp",
                       "event_start_timestamp", "ApplicationID", "OfferID"]]

# converting to MDLs
for i, row in sample_df.iterrows():
    if row["event_activity"] in ["O_Returned", "O_Sent (mail and online)", "O_Sent (online only)"]:
        sample_df.at[i, 'ApplicationID'] = None
    if row["event_activity"] not in ["O_Create", "O_Create Offer", "O_Returned", "O_Sent (mail and online)", "O_Sent (online only)", "O_Cancelled", "O_Accepted", "W_Call after offers"]:
        sample_df.at[i, 'OfferID'] = None
    if row["ApplicationID"] is not None:
        sample_df.at[i, 'ApplicationID'] = [sample_df.at[i, 'ApplicationID']]
    if row["OfferID"] is not None:
        sample_df.at[i, 'OfferID'] = [sample_df.at[i, 'OfferID']]

print(sample_df)
sample_df.to_csv(
    "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-MDL.csv")

event_df = sample_df
ots = ["ApplicationID", "OfferID"]

# filename = "BPI2017.csv"
# ots = ["application", "offer"]

# event_df = pd.read_csv(filename, sep=',')[:2000]
# for ot in ots:
#     event_df[ot] = event_df[ot].map(
#         lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])


def remove_nan(l):
    return [x for x in l if type(x) == str]


for ot in ots:
    event_df[ot] = event_df[ot].apply(remove_nan)
print(event_df)
event_df["event_id"] = list(range(0, len(event_df)))
event_df.index = list(range(0, len(event_df)))
event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
ocel = OCEL(event_df, ots)
print("Number of cases: "+str(len(ocel.cases)))
print("Number of variants: "+str(len(ocel.variants)))
print(ocel.log)
print(ocel.variant_frequency)
print(ocel.variants)
# sub_ocel = trace_filtering.filter_infrequent_traces(ocel, 0.3)
# ocpn = ocpn_discovery_factory.apply(sub_ocel, parameters={"debug": False})
# contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(ocel)
# precision, fitness = precision_fitness_evaluator.apply(
#     ocel, ocpn, contexts=contexts, bindings=bindings)
# print("Precision: "+str(precision))
# print("Fitness: "+str(fitness))

# variant filtering
filtered_log = ocel.log.loc[ocel.log["event_variant"] < 3]
print(filtered_log)

# exporting
filtered_log.to_csv(
    "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top3.csv")
