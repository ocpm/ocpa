import ocpa.objects.log.importer.ocel.factory as ocel_import_factory
from ocpa.objects.log.importer.mdl.util import succint_mdl_to_exploded_mdl
import ocel


def execute_script():
    log = ocel.import_log("./log.xmlocel")
    ocel.export_log(log, "log.jsonocel")


if __name__ == "__main__":
    # execute_script()

    df, _ = ocel_import_factory.apply(
        f"log.jsonocel", parameters={'return_df': True})
    df.to_csv('log.csv')
    exploded_df = succint_mdl_to_exploded_mdl(df)
    exploded_df.to_csv('exploded_log.csv')
