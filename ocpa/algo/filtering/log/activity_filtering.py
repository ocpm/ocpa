from collections import Counter
def filter_infrequent_activities(ocel, threshold):
    #how to deal with multiple events?
    activity_distribution = Counter(ocel["event_activity"].values.tolist())
    activities, frequencies = map(list,zip(*[(a,f/len(list(activity_distribution.elements()))) for (a,f) in activity_distribution.most_common()]))
    freq_acc=[sum(frequencies[0:i+1]) for i in range(0,len(frequencies))]
    filtered_activities = [activities[i] for i in range(0,len(activities)) if threshold  > freq_acc[i] ]
    sublog = ocel[ocel["event_activity"].isin(filtered_activities)]
    return sublog