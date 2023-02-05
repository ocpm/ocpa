# from ocpa.objects.oc_petri_net.obj import EnhancedObjectCentricPetriNet
from ocpa.algo.conformance.constraint_monitoring.versions import log_based
from ocpa.algo.conformance.constraint_monitoring.versions import extensive_log_based
from ocpa.objects.log.ocel import OCEL
from typing import Dict


# MODEL_BASED = "model_based"
LOG_BASED = "log_based"
EXTENSIVE = "extensive_log_based"
VERSIONS = {
    LOG_BASED: log_based.apply,
    EXTENSIVE: extensive_log_based.apply
}


def apply(cg, ocel: OCEL, variant=EXTENSIVE, parameters=None):
    '''
    Monitoring the violation of constraints by analyzing object-centric event logs. The constraints are represented as object-centric constraint graphs. For each violation of the constraint, it provides the analysis of the violation.

    :param cg: Object-centric constraint graph
    :type ocpn: :class:`OCPN <ocpa.objects.graph.constraint_graph.ConstraintGraph>`

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param diag: performance measures per activity, e.g., {'Act1': {'Measure1': value, 'Measure2: value, ...}, 'Act2': {...}, ...}. Value has different formats depending on the performance measure, e.g., the one for 'act_freq' is Integer, the one for 'object_count', 'pooling_time', 'lagging_time', and 'synchronization_time' is a nested dictionary (e.g., {'ObjectType1': {'mean': Real, 'median': Real, ...}, 'ObjectType2': {...}, ...}), the one for 'waiting_time', 'service_time', 'sojourn_time', and 'flow_time' is a dictionary (e.g., {'mean': Real, 'median': Real, ...}).
    :type ocel: Dict

    :return: Violated, A List of diagnostics for the violation. Violated is a Boolean value where True denotes that the constraint is violated and False denotes that the constraint is not violated. Diagnostics explains why the constraint is violated by analyzing each edge of the constraint graph.
    :rtype: Boolean, List

    '''
    return VERSIONS[variant](cg, ocel, parameters=parameters)
