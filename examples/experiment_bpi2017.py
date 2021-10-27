import pandas as pd
from ocpa.objects.log.importer.mdl import factory as mdl_import_factory
from ocpa.objects.log.importer.mdl.factory import succint_mdl_to_exploded_mdl
filename = "/Users/gyunam/Documents/ocpa-core/example_logs/mdl/BPI2017-Top10.csv"
ots = ["A", "O"]
df = pd.read_csv(filename)
del df["Unnamed: 0"]
del df["EventID"]

df = mdl_import_factory.apply(df, parameters={'return_df': True})
# df.rename(columns={'CaseID': "event_case"}, inplace=True)
# df = succint_mdl_to_exploded_mdl(df)
# print(df)
# df.to_csv("../example_logs/mdl/BPI2017-Top10-exploded.csv")

added = []
for i, row in df.iterrows():
    offer_list = df.at[i, 'O']
    offer_list = [y.strip() for y in offer_list.split(
        ',')] if isinstance(offer_list, str) else []
    for i in range(len(offer_list)):
        if i == 0:
            continue
        else:
            row["event_id"] += ("-" + str(i))
            added.append(row)

df2 = pd.DataFrame.from_records(added)
print(df)
df3 = pd.concat([df, df2], ignore_index=True)
df3.reset_index(inplace=True, drop=True)
df3.sort_values(by=["CaseID", "event_timestamp"], inplace=True)
print(df3)
df3.to_csv("../example_logs/mdl/BPI2017-Top10-flattened.csv")
