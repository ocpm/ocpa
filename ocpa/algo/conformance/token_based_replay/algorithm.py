import ocpa.algo.conformance.token_based_replay.variants.flattened_replay as flattened_replay
import ocpa.algo.conformance.token_based_replay.variants.object_centric_replay as object_centric_replay

def apply(ocel,ocpn,method='object_centric',parameters=None):
    if method == 'object_centric':
        return object_centric_replay.apply(ocel,ocpn,parameters=parameters)
    elif method == 'flattened':
        return flattened_replay.apply(ocel,ocpn,parameters=parameters)
    else:
        raise ValueError("Method not defined")