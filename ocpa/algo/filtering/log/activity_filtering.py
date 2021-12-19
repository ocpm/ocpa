from collections import Counter
from ocpa.objects.log.obj import OCEL

def filter_infrequent_activities(ocel, threshold):
    #how to deal with multiple events?
    activity_distribution = Counter(ocel.log["event_activity"].values.tolist())
    activities, frequencies = map(list,zip(*[(a,f/len(list(activity_distribution.elements()))) for (a,f) in activity_distribution.most_common()]))
    freq_acc=[sum(frequencies[0:i+1]) for i in range(0,len(frequencies))]
    last_filtered_activity = len(freq_acc) - 1
    for i in range(0, len(freq_acc)):
        if freq_acc[i] > threshold:
            last_filtered_activity = i
            break


    filtered_activities = activities[:last_filtered_activity+1]#[activities[i] for i in range(0,len(activities)) if threshold  >= freq_acc[i] ]
    sublog = ocel.log[ocel.log["event_activity"].isin(filtered_activities)].copy()
    return OCEL(sublog, object_types=ocel.object_types, execution_extraction=ocel._execution_extraction, leading_object_type=ocel._leading_type)