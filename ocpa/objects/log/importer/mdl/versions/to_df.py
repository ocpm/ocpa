import pandas as pd
from ast import literal_eval
import math


def apply(all_df, parameters=None):
    if parameters is None:
        raise ValueError("Specify parsing parameters")

    # eve_cols = [x for x in all_df.columns if x.startswith("event_")]
    # obj_cols = [x for x in all_df.columns if not x.startswith("event_")]
    obj_cols = parameters['obj_names']
    df = all_df

    def _eval(x):
        if x == 'set()':
            x = '{}'
        if type(x) == float and math.isnan(x):
            return None
        else:
            return literal_eval(x)

    if obj_cols:
        for c in obj_cols:
            df[c] = df[c].apply(_eval)

    rename_dict = {}
    for col in [x for x in all_df.columns if not x.startswith("event_")]:
        if col not in obj_cols:
            rename_dict[col] = 'event_' + col
    df.rename(columns=rename_dict, inplace=True)

    df[parameters['time_name']] = pd.to_datetime(df[parameters['time_name']])
    if "start_time" in parameters:
        df["event_start_timestamp"] = pd.to_datetime(
            df[parameters['start_time']])
    df = df.dropna(subset=["event_id"])
    df["event_id"] = df["event_id"].astype(str)
    df.type = "succint"
    return df
