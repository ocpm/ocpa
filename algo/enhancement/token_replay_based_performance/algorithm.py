from ocpa.algo.enhancement.token_replay_based_performance.versions import opera
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.log.ocel import OCEL
OPERA = "opera"

VERSIONS = {OPERA: opera.apply}


def apply(ocpn: ObjectCentricPetriNet, ocel: OCEL, variant=OPERA, parameters=None):
    '''
    Computing object-centric performance measures using object-centric event logs. It is model-based approach where we 1) discover an object-centric Petri net, 2) replay an object-centric event log, and 3) compute object-centric performance measures based on the replay history. It provides object-centric performance measures such as lagging, pooling, synchronization, and flow times, along with traditional performance measures such as waiting, service, and sojourn times.

    :param ocpn: Object-centric Petri net
    :type ocpn: :class:`OCPN <ocpa.objects.oc_petri_net.obj.ObjectCentricPetriNet>`

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param measures: A list of performance measures to analyze. 'act_freq': Activity Frequency, 'arc_freq': Arc Frequency, 'object_count': Object Count, 'waiting_time': Waiting Time, 'service_time': Service Time, 'sojourn_time': Sojourn Time, 'synchronization_time': Synchronization Time, 'pooling_time': Pooling Time, 'lagging_time': Lagging Time, 'flow_time': Flow Time.
    :type measures: List

    :param agg: A list of aggregations. 'mean': Mean, 'median': Median, 'stdev': Standard Deviation, 'sum': Summation, 'min': Minimum, 'max': Maximum
    :type agg: List

    :return: performance measures per activity, e.g., {'Act1': {'Measure1': value, 'Measure2: value, ...}, 'Act2': {...}, ...}. Value has different formats depending on the performance measure, e.g., the one for 'act_freq' is Integer, the one for 'object_count', 'pooling_time', 'lagging_time', and 'synchronization_time' is a nested dictionary (e.g., {'ObjectType1': {'mean': Real, 'median': Real, ...}, 'ObjectType2': {...}, ...}), the one for 'waiting_time', 'service_time', 'sojourn_time', and 'flow_time' is a dictionary (e.g., {'mean': Real, 'median': Real, ...}).
    :rtype: Dict

    '''
    return VERSIONS[variant](ocpn, ocel, parameters=parameters)
