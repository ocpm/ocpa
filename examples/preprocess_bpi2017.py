from pm4py.objects.conversion.log import converter as log_converter
import math
import pandas as pd
from ocpa.objects.ocel.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator


# # Preprocess: removing duplicated events
# print(len(df))
# df.drop_duplicates(
#     subset=['event', 'completeTime'], inplace=True)
# print(len(df))
# df.to_csv(
#     "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full-remove_duplicates.csv")


# filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full-remove_duplicates.csv"
# df = pd.read_csv(filename)

# filter only applications with two create offers
# activity_mapping = df.groupby("case")["event"].apply(list)
# print(type(activity_mapping))
# selected_cases = []
# for case, acts in activity_mapping.items():
#     if acts.count("O_Create Offer") > 1:
#         selected_cases.append(case)
# df = df[df["case"].isin(selected_cases)]
# print(df)
# df.to_csv("../example_logs/mdl/Full-remove_duplicates-offers.csv")

# filter only a_denied/cancelled cases to have variable arcs
# then, unnormalize the data
filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full-remove_duplicates-offers.csv"
df = pd.read_csv(filename)
offer_mapping = df.groupby("case")["OfferID"].apply(set)
print(offer_mapping)

# filter only applications with a_denied or a_cancelled
activity_mapping = df.groupby("case")["event"].apply(list)
selected_cases = []
for case, acts in activity_mapping.items():
    # if "A_Denied" in acts:
    #     selected_cases.append(case)
    if "A_Cancelled" in acts:
        selected_cases.append(case)
selected_cases = set(selected_cases)
df = df[df["case"].isin(selected_cases)]
df.to_csv("../example_logs/mdl/Full-remove_duplicates-offers-deny-cancell.csv")

# filter A_Complete since it has no meaning (always after W_Call after offers)
df = df.loc[df["event"] != "A_Complete"]

# filter A_Concept since it has no meaning (always after W_Complete application)
df = df.loc[df["event"] != "A_Concept"]

# filter A_Validating since it has no meaning (always after W_Validate application)
df = df.loc[df["event"] != "A_Validating"]
df = df.loc[df["event"] != "A_Incomplete"]
df = df.loc[df["event"] != "O_Created"]


def assign_offers(case):
    return {x for x in offer_mapping[case] if type(x) != float}


df.loc[df["event"] == "A_Denied", "OfferID"] = df.loc[df["event"]
                                                      == "A_Denied", "case"].apply(assign_offers)
df.loc[df["event"] == "A_Cancelled", "OfferID"] = df.loc[df["event"]
                                                         == "A_Cancelled", "case"].apply(assign_offers)


# def filt(x):
#     print(x)
#     return True if "," in str(x) else False


# df = df.loc[df["OfferID"].apply(filt)]
# print(df["OfferID"])

# sampling
sampling = True
if sampling == True:
    applications = set(df["case"])
    num_apps = len(applications)
    sample_size = int(num_apps*0.1)
    samples = list(applications)[:sample_size]
    sample_df = df.loc[df["case"].isin(samples)]
    sample_df.reset_index(inplace=True)

else:
    sample_df = df
    sample_df.reset_index(inplace=True)

# renaming column names
sample_df["CaseID"] = sample_df["case"]
sample_df = sample_df.rename(columns={"index": "event_id", "case": "A", "OfferID": "O", "event": "event_activity",
                                      "completeTime": "event_timestamp", "startTime": "event_start_timestamp"})
# filtering relevant columns
sample_df = sample_df[["event_id", "event_activity", "event_timestamp",
                       "event_start_timestamp", "A", "O", "CaseID", "EventID"]]

# converting to MDLs
for i, row in sample_df.iterrows():
    if row["event_activity"] in ["O_Returned", "O_Created", "O_Sent (mail and online)", "O_Sent (online only)", "O_Cancelled", "W_Call after offers"]:
        row["A"] = None
    if row["event_activity"] not in ["O_Created", "O_Returned", "O_Sent (mail and online)", "O_Sent (online only)", "O_Cancelled", "O_Accepted", "W_Call after offers", "A_Denied", "A_Cancelled", "O_Refused"]:
        row["O"] = None
    # offer id for create offer is stored as eventid
    if row["event_activity"] == "O_Create Offer":
        sample_df.at[i, 'O'] = sample_df.at[i, 'EventID']
    # filter nan values
    if type(row["A"]) == float and math.isnan(row["A"]):
        row["A"] = None
    if type(row["O"]) == float and math.isnan(row["O"]):
        row["O"] = None

    if row["A"] is not None:
        if type(row["A"]) == set:
            continue
        elif type(row["A"]) == str:
            sample_df.at[i, 'A'] = {
                sample_df.at[i, 'A']}
        # elif type(row["A"]) == float:
        #     sample_df.at[i, 'A'] = None
        else:
            raise ValueError("Cannot recognize the type of A")
    else:
        sample_df.at[i, 'A'] = ''
    if row["O"] is not None:
        if type(row["O"]) == set:
            continue
        elif type(row["O"]) == str:
            sample_df.at[i, 'O'] = {sample_df.at[i, 'O']}
        # elif type(row["O"]) == float:
        #     sample_df.at[i, 'O'] = None
        else:
            raise ValueError(
                "Cannot recognize the type of O: {}".format(row["O"]))
    else:
        sample_df.at[i, 'O'] = ''

renaming_activity = {
    "A_Create Application": "Create application",
    "A_Submitted": "Submit",
    "W_Handle leads": "Handle leads",
    "A_Accepted": "Accept",
    "W_Call after offers": "Call",
    "O_Cancelled": "Cancel offer",
    "O_Create Offer": "Create offer",
    "O_Sent (mail and online)": "Send",
    "W_Complete application": "Complete",
    "A_Cancelled": "Cancel application",
    "O_Returned": "Return",
}
sample_df.replace({"event_activity": renaming_activity}, inplace=True)

sample_df.to_csv(
    "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-MDL.csv")

event_df = sample_df
ots = ["A", "O"]

# filename = "BPI2017.csv"
# ots = ["application", "offer"]

# event_df = pd.read_csv(filename, sep=',')[:2000]
# for ot in ots:
#     event_df[ot] = event_df[ot].map(
#         lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])


def remove_nan(l):
    return {x for x in l if type(x) == str} if type(l) == set else l


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
filtered_log = ocel.log.loc[ocel.log["event_variant"] < 10]
print(filtered_log)

# exporting
filtered_log = filtered_log.astype(str)
filtered_log.to_csv(
    "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top10-2.csv")
