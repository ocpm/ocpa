import statistics
from ocpa.objects.log.importer.csv.util import succint_mdl_to_exploded_mdl
from pm4py.objects.conversion.log import converter as log_conv_factory

AGG_MAP = {
    'avg': statistics.mean,
    'med': statistics.median,
    'std': statistics.stdev,
    'sum': sum,
    'min': min,
    'max': max
}


def project_log(df, persp, parameters=None):
    if parameters is None:
        parameters = {}

    try:
        if df.type == "succint":
            df = succint_mdl_to_exploded_mdl(df)
            df.type = "exploded"
    except:
        pass
    cols = [x for x in df.columns if x.startswith("event_") or x == persp]
    df = df[cols].dropna(subset=[persp])

    renaming = {}
    renaming["event_activity"] = "concept:name"
    renaming["event_timestamp"] = "time:timestamp"
    renaming[persp] = "case:concept:name"

    df = df.rename(columns=renaming)
    df = df.dropna(subset=["concept:name"])
    log = log_conv_factory.apply(df)

    return log


def project_log_with_object_count(df, persp, parameters=None):
    if parameters is None:
        parameters = {}

    try:
        if df.type == "succint":
            df = succint_mdl_to_exploded_mdl(df)
            df.type = "exploded"
    except:
        pass

    cols = [x for x in df.columns if x.startswith("event_") or x == persp]
    df = df[cols].dropna(subset=[persp])

    df = df.groupby(["event_activity", persp]).first()
    values = df.groupby(["event_id", "event_activity"]).size().to_dict()

    ret = {}
    for v in values:
        if not v[1] in ret:
            ret[v[1]] = []
        ret[v[1]].append(values[v])

    for k in ret:
        ret[k] = sorted(ret[k])

    return ret
