import pandas as pd
from ast import literal_eval
import math


def apply(filepath, parameters=None):
    if parameters is None:
        raise ValueError("Specify parsing parameters")
    df = pd.read_csv(filepath, parameters["sep"])
    # eve_cols = [x for x in df.columns if x.startswith("event_")]
    # obj_cols = [x for x in df.columns if not x.startswith("event_")]
    obj_cols = parameters['obj_names']

    def _eval(x):
        if x == 'set()':
            x = {}
        if type(x) == float and math.isnan(x):
            return []
        else:
            return literal_eval(x)

    if obj_cols:
        for c in obj_cols:
            df[c] = df[c].apply(_eval)

    df['activity'] = df[parameters['act_name']]
    del df[parameters['act_name']]
    df['timestamp'] = df[parameters['time_name']]
    del df[parameters['time_name']]
    if "start_timestamp" in parameters:
        df['start_timestamp'] = df[parameters['start_timestamp']]
        del df[parameters['start_timestamp']]

    rename_dict = {}
    for col in [x for x in df.columns if not x.startswith("event_")]:
        if col not in obj_cols:
            rename_dict[col] = 'event_' + col
    df.rename(columns=rename_dict, inplace=True)

    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    df = df.dropna(subset=["event_id"])
    df["event_id"] = df["event_id"].astype(str)
    #df.type = "succint"
    return df
