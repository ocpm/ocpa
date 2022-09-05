from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring

filename = "../../sample_logs/jsonocel/p2p-normal.jsonocel"
ocel = ocel_import_factory.apply(filename)
activities = list(set(ocel.log.log["event_activity"].tolist()))
feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
               (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
               (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
              [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities]
feature_storage = predictive_monitoring.apply(ocel, feature_set, [])