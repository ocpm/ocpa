from ocpa.algo.discovery.ocpn.versions import inductive_and_tr
from ocpa.objects.log.obj import OCEL
from ocpa.objects.log.obj import ObjectCentricEventLog
import ocpa.objects.log.converter.factory as convert_factory

INDUCTIVE_AND_TR = "inductive_and_tr"

VERSIONS = {INDUCTIVE_AND_TR: inductive_and_tr.apply}


def apply(ocel, variant=INDUCTIVE_AND_TR, parameters=None):
    if type(ocel) == OCEL:
        return VERSIONS[variant](ocel.log, parameters=parameters)
    if type(ocel) == ObjectCentricEventLog:
        df, _ = convert_factory.apply(ocel, variant='json_to_mdl')
        return VERSIONS[variant](df, parameters=parameters)
    else:
        return VERSIONS[variant](ocel, parameters=parameters)
