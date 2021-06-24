from ocpa.objects.log.importer.mdl import factory as mdl_import_factory


def apply(df, persp, parameters=None):
    if parameters is None:
        parameters = {}

    try:
        if df.type == "succint":
            df = mdl_import_factory.succint_mdl_to_exploded_mdl(df)
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
