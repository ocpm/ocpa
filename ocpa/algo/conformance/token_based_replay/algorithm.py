from ocpa.algo.conformance.token_based_replay.versions import token_based_replay

TOKEN_BASED_REPLAY = "token_based_replay"

VERSIONS = {TOKEN_BASED_REPLAY: token_based_replay.apply}


def apply(ocpn, df, variant=TOKEN_BASED_REPLAY, parameters=None):
    return VERSIONS[variant](ocpn, df, parameters=parameters)
