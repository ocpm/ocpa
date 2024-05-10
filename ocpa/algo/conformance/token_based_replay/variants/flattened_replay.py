import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as flattened_log_replay
from ocpa.algo.conformance.token_based_replay.utils import log_ocpa2pm4py as log_converter
from ocpa.algo.conformance.token_based_replay.utils import pn_ocpa2pm4py as pn_converter

def apply(ocel,ocpn,parameters=None):
    '''
    Based on the traditional token-based replay method implemented in pm4py
    '''
    from pm4py.util import constants
    from pm4py.util.xes_constants import DEFAULT_NAME_KEY
    from pm4py.algo.conformance.tokenreplay.variants import token_replay
    ocel = log_converter(ocel)
    ocpn = pn_converter(ocpn)
    pn_dict, el_dict = {}, {}
    p,c,m,r = 0,0,0,0
    for ot in ocpn['object_types']:
        pn_dict[ot] = ocpn['petri_nets'][ot]
        el_dict[ot] = pm4py.ocel_flattening(ocel, ot)  
    for ot in ocpn['object_types']:        
        token_replay_variant = flattened_log_replay.Variants.TOKEN_REPLAY
        if parameters == None:
            parameters = {token_replay.Parameters.ACTIVITY_KEY:DEFAULT_NAME_KEY,
                         token_replay.Parameters.CONSIDER_REMAINING_IN_FITNESS:True,
                         token_replay.Parameters.CLEANING_TOKEN_FLOOD:True,
                         token_replay.Parameters.CASE_ID_KEY:constants.CASE_CONCEPT_NAME}
        aligned_traces = flattened_log_replay.apply(el_dict[ot], pn_dict[ot][0], pn_dict[ot][1], pn_dict[ot][2],variant=token_replay_variant,parameters=parameters)
        p += sum([x["produced_tokens"] for x in aligned_traces])
        c += sum([x["consumed_tokens"] for x in aligned_traces])
        r += sum([x["remaining_tokens"] for x in aligned_traces])
        m += sum([x["missing_tokens"] for x in aligned_traces])
    if p==0 or c==0:
        raise ValueError('No tokens are consumed or produced during the replay')
    result = {'fitness':0.5*(1-m/c)+0.5*(1-r/p),'p':p,'c':c,'r':r,'m':m}
    return result
