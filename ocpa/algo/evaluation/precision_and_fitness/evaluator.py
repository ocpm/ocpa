from ocpa.algo.evaluation.precision_and_fitness.variants import replay_context
import ocpa.algo.evaluation.precision_and_fitness.utils as utils


def apply(ocel,ocpn,contexts=None,bindings=None):
    object_types = ocel.object_types
    if contexts == None or bindings == None:
        contexts, bindings = utils.calculate_contexts_and_bindings(ocel)
    en_l =  replay_context.enabled_log_activities(ocel,contexts)
    en_m =  replay_context.enabled_model_activities_multiprocessing(contexts,bindings,ocpn,object_types)
    precision, skipped_events, fitness =  replay_context.calculate_precision_and_fitness(ocel,contexts,en_l,en_m)
    return precision, fitness
    