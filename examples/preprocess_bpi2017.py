import pandas as pd

filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Full.csv"
df = pd.read_csv(filename)

# sampling
sampling = False
if sampling == True:
    applications = set(df["case"])
    num_apps = len(applications)
    sample_size = int(num_apps*0.001)
    samples = list(applications)[:sample_size]
    sample_df = df.loc[df["case"].isin(samples)]
    sample_df.reset_index(inplace=True)

else:
    sample_df = df

# renaming column names
sample_df = sample_df.rename(columns={"index": "event_id", "case": "ApplicationID", "event": "event_activity",
                                      "completeTime": "event_timestamp", "startTime": "event_start_timestamp"})
# filtering relevant columns
sample_df = sample_df[["event_id", "event_activity", "event_timestamp",
                       "event_start_timestamp", "ApplicationID", "OfferID"]]

# converting to MDLs
for i, row in sample_df.iterrows():
    if row["event_activity"] in ["O_Returned", "O_Sent"]:
        sample_df.at[i, 'ApplicationID'] = None
    if row["event_activity"] in ["O_Create"]:
        sample_df.at[i, 'OfferID'] = None
    if row["ApplicationID"] is not None:
        sample_df.at[i, 'ApplicationID'] = [row["ApplicationID"]]
    if row["OfferID"] is not None:
        sample_df.at[i, 'OfferID'] = [row["OfferID"]]
print(sample_df)

# exporting
sample_df.to_csv(
    "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/Sample.csv")
