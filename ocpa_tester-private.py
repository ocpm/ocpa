from ocpa.objects.log.obj import OCEL
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
import pandas as pd
import ocpa.algo.filtering.log.trace_filtering as trace_filtering
import ocpa.algo.evaluation.precision_and_fitness.utils as evaluation_utils
import ocpa.algo.evaluation.precision_and_fitness.evaluator as precision_fitness_evaluator
import ocpa.algo.feature_extraction.factory as feature_extraction
# TODO: Preprocessing and conversion from other types of OCEL
filename = "BPI2017.csv"
ots = ["application", "offer"]


event_df = pd.read_csv(filename, sep=',')[:27]
print(event_df)
for ot in ots:
    event_df[ot] = event_df[ot].map(
        lambda x: [y.strip() for y in x.split(',')] if isinstance(x, str) else [])
event_df["event_id"] = list(range(0, len(event_df)))
event_df.index = list(range(0, len(event_df)))
event_df["event_id"] = event_df["event_id"].astype(float).astype(int)
ocel = OCEL(event_df, ots)
###this is needed to extract the features into the feature storage
feature_storage = feature_extraction.apply(ocel,[feature_extraction.EVENT_NUM_OF_OBJECTS],[feature_extraction.EXECUTION_NUM_OF_EVENTS,feature_extraction.EXECUTION_NUM_OF_END_EVENTS])


####example of how the feature storage looks like
for f_g in feature_storage.feature_graphs:
    print("Next Feature Graph")
    for e in f_g.edges:
        print("Edge: from "+str(e.source)+" to "+str(e.target)+" with objects "+str(e.objects))
    print("Execution (global) attributes:")
    print(f_g.attributes)
    print("Event attributes:")
    for n in f_g.nodes:
        print("for event: "+str(n.event_id))
        print(n.attributes)
        print(n.objects)

#for going through the graph


# print("Number of cases: "+str(len(ocel.cases)))
# print("Number of variants: "+str(len(ocel.variants)))
# print(ocel.variant_frequency)
# sub_ocel = trace_filtering.filter_infrequent_traces(ocel, 0.3)
# ocpn = ocpn_discovery_factory.apply(sub_ocel, parameters={"debug": False})
# contexts, bindings = evaluation_utils.calculate_contexts_and_bindings(ocel)
# precision, fitness = precision_fitness_evaluator.apply(
#     ocel, ocpn, contexts=contexts, bindings=bindings)
# print("Precision: "+str(precision))
# print("Fitness: "+str(fitness))

