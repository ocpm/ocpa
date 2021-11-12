<<<<<<< HEAD
from ocpa.objects.log.importer.mdl import factory as mdl_import_factory
=======
from ocpa.objects.log.importer.mdl.util import succint_mdl_to_exploded_mdl
>>>>>>> origin/Publishing


def apply(df, persp, parameters=None):
    if parameters is None:
        parameters = {}

    try:
        if df.type == "succint":
<<<<<<< HEAD
            df = mdl_import_factory.succint_mdl_to_exploded_mdl(df)
=======
            df = succint_mdl_to_exploded_mdl(df)
>>>>>>> origin/Publishing
            df.type = "exploded"
    except:
        pass

    cols = [x for x in df.columns if x.startswith("event_") or x == persp]
    df = df[cols].dropna(subset=[persp])

    return dict(df.groupby("event_id").first()["event_activity"].value_counts())
