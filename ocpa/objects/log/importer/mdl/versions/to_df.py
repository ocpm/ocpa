import pandas as pd
from ast import literal_eval


def apply(all_df, parameters=None):
    if parameters is None:
        parameters = {}

    eve_cols = [x for x in all_df.columns if x.startswith("event_")]
    obj_cols = [x for x in all_df.columns if not x.startswith("event_")]
    df = all_df

    def _eval(x):
        try:
            return literal_eval(x.replace('set()', '{}'))
        except:
            return None

    if obj_cols:
        for c in obj_cols:
            df[c] = df[c].apply(_eval)

    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    if "event_start_timestamp" in df.columns:
        df["event_start_timestamp"] = pd.to_datetime(
            df["event_start_timestamp"])
    df = df.dropna(subset=["event_id"])
    df["event_id"] = df["event_id"].astype(str)
    df.type = "succint"
    return df
