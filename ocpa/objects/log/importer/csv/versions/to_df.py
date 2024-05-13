import ast
import math

import pandas as pd


def apply(
    filepath: str, parameters: dict = None, file_path_object_attribute_table=None
) -> pd.DataFrame:
    if parameters is None:
        raise ValueError("Specify parsing parameters")
    df = pd.read_csv(filepath, sep=parameters["sep"])
    obj_cols = parameters["obj_names"]

    def _eval(x):
        if x == "set()":
            return []
        elif type(x) == float and math.isnan(x):
            return []
        else:
            return ast.literal_eval(x)

    df_ocel = pd.DataFrame()

    if obj_cols:
        for c in obj_cols:
            df_ocel[c] = df[c].apply(_eval)

    # if "event_id" in df.columns:
    #     df_ocel["event_id"] = df["event_id"].astype(str)
    # else:
    df_ocel["event_id"] = [str(i) for i in range(len(df))]
    df_ocel["event_activity"] = df[parameters["act_name"]]
    df_ocel["event_timestamp"] = pd.to_datetime(df[parameters["time_name"]])
    df_ocel.sort_values(by="event_timestamp", inplace=True)
    if "start_timestamp" in parameters:
        df_ocel["event_start_timestamp"] = pd.to_datetime(
            df[parameters["start_timestamp"]]
        )
    else:
        df_ocel["event_start_timestamp"] = pd.to_datetime(df[parameters["time_name"]])

    for val_name in parameters["val_names"]:
        if val_name.startswith("event_"):
            df_ocel[val_name] = df[val_name]
        else:
            df_ocel[("event_" + val_name)] = df[val_name]

    if "obj_val_names" in parameters:
        for obj_val_name in parameters["val_names"]:
            df_ocel[obj_val_name] = df[parameters[obj_val_name]]
    return df_ocel
