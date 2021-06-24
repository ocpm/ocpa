import pandas as pd
from copy import deepcopy
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics


def apply(all_df, return_obj_dataframe=False, parameters=None):
    if parameters is None:
        parameters = {}

    eve_cols = [x for x in all_df.columns if not x.startswith("object_")]
    obj_cols = [x for x in all_df.columns if x.startswith("object_")]
    df = all_df[eve_cols]
    obj_df = pd.DataFrame()
    if obj_cols:
        obj_df = all_df[obj_cols]
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    if "event_start_timestamp" in df.columns:
        df["event_start_timestamp"] = pd.to_datetime(
            df["event_start_timestamp"])
    df = df.dropna(subset=["event_id"])
    df["event_id"] = df["event_id"].astype(str)
    df.type = "succint"

    if return_obj_dataframe:
        obj_df = obj_df.dropna(subset=["object_id"])
        return df, obj_df

    return df


def filter_by_timestamp(df, start_timestamp=None, end_timestamp=None):
    if start_timestamp is not None:
        df = df.loc[df["event_timestamp"] >= start_timestamp]
    if end_timestamp is not None:
        df = df.loc[df["event_timestamp"] <= end_timestamp]
    return df


def filter_object_df_by_object_ids(df, ids):
    df = df.loc[df["object_id"].isin(ids)]
    return df



def succint_stream_to_exploded_stream(stream):
    new_stream = []

    for ev in stream:
        keys = set(ev.keys())

        event_keys = [k for k in keys if k.startswith("event_")]
        object_keys = [k for k in keys if not k in event_keys]

        basic_event = {k: ev[k] for k in event_keys}

        for k in object_keys:
            if type(ev[k]) is str:
                if ev[k][0] == "[":
                    ev[k] = eval(ev[k])
                    #ev[k] = ev[k][1:-1].split(",")
            values = ev[k]
            if values is not None:
            #if values is not None and len(values) > 0:
                if not (str(values).lower() == "nan" or str(values).lower() == "nat"):
                    for v in values:
                        event = deepcopy(basic_event)
                        event[k] = v
                        new_stream.append(event)

    return new_stream

def succint_mdl_to_exploded_mdl(df):
    stream = df.to_dict('r')

    exploded_stream = succint_stream_to_exploded_stream(stream)

    df = pd.DataFrame(exploded_stream)
    df.type = "exploded"

    return df

def clean_frequency(df, min_acti_freq=0):
    try:
        if df.type == "succint":
            df = succint_mdl_to_exploded_mdl(df)
    except:
        pass
    activ = dict(df.groupby("event_id").first()["event_activity"].value_counts())
    activ = [x for x,y in activ.items() if y >= min_acti_freq]
    return df[df["event_activity"].isin(activ)]

def filter_paths(df, paths, parameters=None):
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    ----------
    df
        Dataframe
    paths
        Paths to filter on
    parameters
        Possible parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            attribute_key -> Attribute we want to filter
            positive -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    try:
        if df.type == "succint":
            df = succint_mdl_to_exploded_mdl(df)
    except:
        pass
    if parameters is None:
        parameters = {}
    paths = [path[0] + "," + path[1] for path in paths]
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    df = df.sort_values([case_id_glue, "event_timestamp"])
    positive = parameters["positive"] if "positive" in parameters else True
    filt_df = df[[case_id_glue, attribute_key, "event_id"]]
    filt_dif_shifted = filt_df.shift(-1)
    filt_dif_shifted.columns = [str(col) + '_2' for col in filt_dif_shifted.columns]
    stacked_df = pd.concat([filt_df, filt_dif_shifted], axis=1)
    stacked_df["@@path"] = stacked_df[attribute_key] + "," + stacked_df[attribute_key + "_2"]
    stacked_df = stacked_df[stacked_df["@@path"].isin(paths)]
    i1 = df.set_index("event_id").index
    i2 = stacked_df.set_index("event_id").index
    i3 = stacked_df.set_index("event_id_2").index
    if positive:
        return df[i1.isin(i2) | i1.isin(i3)]
    else:
        return df[~i1.isin(i2) & ~i1.isin(i3)]


def clean_arc_frequency(df, min_freq=0):
    if min_freq > 0:
        persps = [x for x in df.columns if not x.startswith("event_")]
        collation = []
        for persp in persps:
            red_df = df.dropna(subset=[persp])
            prevlen = len(df)
            while True:
                dfg = df_statistics.get_dfg_graph(red_df, activity_key="event_activity", timestamp_key="event_timestamp", case_id_glue=persp)
                dfg = [x for x in dfg if dfg[x] >= min_freq]
                param = {}
                param[PARAMETER_CONSTANT_CASEID_KEY] = persp
                param[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = "event_activity"
                red_df = filter_paths(red_df, dfg, parameters=param)
                thislen = len(red_df)
                dfg = df_statistics.get_dfg_graph(red_df, activity_key="event_activity", timestamp_key="event_timestamp", case_id_glue=persp)
                if len(dfg) == 0 or min(dfg.values()) >= min_freq or prevlen == thislen:
                    collation.append(red_df)
                    break
                prevlen = thislen
        return pd.concat(collation)
    return df
