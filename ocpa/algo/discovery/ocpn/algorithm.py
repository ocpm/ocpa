from ocpa.algo.discovery.ocpn.versions import inductive_and_tr
<<<<<<< HEAD
=======
from ocpa.objects.log.obj import OCEL
>>>>>>> origin/Publishing

INDUCTIVE_AND_TR = "inductive_and_tr"

VERSIONS = {INDUCTIVE_AND_TR: inductive_and_tr.apply}


<<<<<<< HEAD
def apply(df, variant=INDUCTIVE_AND_TR, parameters=None):
    return VERSIONS[variant](df, parameters=parameters)
=======
def apply(ocel, variant=INDUCTIVE_AND_TR, parameters=None):
    if type(ocel) == OCEL:
        return VERSIONS[variant](ocel.log, parameters=parameters)
    else:
        return VERSIONS[variant](ocel, parameters=parameters)
>>>>>>> origin/Publishing
