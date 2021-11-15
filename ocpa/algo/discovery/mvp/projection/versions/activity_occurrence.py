from ocpa.objects.log.importer.mdl.util import succint_mdl_to_exploded_mdl


def apply(df, persp, parameters=None):
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

    return dict(df.groupby("event_id").first()["event_activity"].value_counts())
