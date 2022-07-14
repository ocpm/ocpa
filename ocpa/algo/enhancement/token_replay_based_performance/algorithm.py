from ocpa.algo.enhancement.token_replay_based_performance.versions import token_based_replay
from ocpa.algo.enhancement.token_replay_based_performance.versions import opera

TOKEN_BASED_REPLAY = "token_based_replay"
OPERA = "opera"

VERSIONS = {TOKEN_BASED_REPLAY: token_based_replay.apply, OPERA: opera.apply}


def apply(ocpn, df, variant=OPERA, parameters=None):
    return VERSIONS[variant](ocpn, df, parameters=parameters)
