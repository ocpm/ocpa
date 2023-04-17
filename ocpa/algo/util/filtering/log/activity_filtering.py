from collections import Counter
from ocpa.objects.log.util import misc as log_util


def filter_infrequent_activities(ocel, threshold):
    '''
    Filters infrequent activities from an OCEL

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param threshold: Kumulative frequency of the most frequent activities to be included.
    :type threshold: float

    :return: Object-centric event log
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''
    activity_distribution = Counter(
        ocel.log.log["event_activity"].values.tolist())
    activities, frequencies = map(list, zip(
        *[(a, f/len(list(activity_distribution.elements()))) for (a, f) in activity_distribution.most_common()]))
    freq_acc = [sum(frequencies[0:i+1]) for i in range(0, len(frequencies))]
    last_filtered_activity = len(freq_acc) - 1
    for i in range(0, len(freq_acc)):
        if freq_acc[i] > threshold:
            last_filtered_activity = i
            break

    filtered_activities = activities[:last_filtered_activity+1]
    sublog = ocel.log.log[ocel.log.log["event_activity"].isin(
        filtered_activities)].copy()
    return log_util.copy_log_from_df(sublog, ocel.parameters)
