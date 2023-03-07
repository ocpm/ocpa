from ocpa.objects.log.util import misc as log_util


def filter_infrequent_variants(ocel, threshold):
    '''
    Filters infrequent variants from an OCEL

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param threshold: Cumulative frequency of the most frequent variants to be included.
    :type threshold: float

    :return: Object-centric event log
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''
    ocel = log_util.copy_log(ocel)
    if threshold > 0.9999:
        return ocel
    v_freq_acc = [sum(ocel.variant_frequencies[0:i+1])
                  for i in range(0, len(ocel.variant_frequencies))]
    last_filtered_variant = len(v_freq_acc)-1
    filtered_variants = []
    for i in range(0, len(v_freq_acc)):
        filtered_variants.append(i)
        if v_freq_acc[i] > threshold:
            last_filtered_variant = i
            break
    # get the relevant objects
    rel_obs = log_util.get_objects_of_variants(ocel, filtered_variants)
    pref_sublog = log_util.remove_object_references(
        ocel.log.log, ocel.object_types, rel_obs)
    sublog = pref_sublog[pref_sublog["event_variant"].apply(
        lambda x: bool(set(x) & set(filtered_variants)))].copy()
    sublog = sublog.drop("event_variant", axis=1)
    sublog = log_util.remove_object_references(
        sublog, ocel.object_types, rel_obs)
    new_log = log_util.copy_log_from_df(sublog, ocel.parameters)
    return new_log
