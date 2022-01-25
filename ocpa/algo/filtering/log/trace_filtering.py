from ocpa.objects.log.obj import OCEL
import pandas as pd

def filter_infrequent_traces(ocel, threshold):
    pd.set_option('display.max_columns', 500)
    ocel = OCEL(ocel.log, object_types=ocel.object_types, execution_extraction=ocel._execution_extraction, leading_object_type=ocel._leading_type)
    if threshold > 0.9999:
        return ocel
    v_freq_acc = [sum(ocel.variant_frequency[0:i+1]) for i in range(0,len(ocel.variant_frequency))]
    last_filtered_variant = len(v_freq_acc)-1
    filtered_variants = []
    for i in range(0,len(v_freq_acc)):
        filtered_variants.append(i)
        if v_freq_acc[i] > threshold:
            last_filtered_variant = i

            break
    #get the relevant objects
    rel_obs = ocel.get_objects_of_variants(filtered_variants)
    ocel.remove_object_references(rel_obs)
    sublog = ocel.log[ocel.log["event_variant"].apply(lambda x: bool( set(x) & set(filtered_variants)))].copy()
    sublog = sublog.drop("event_variant", axis = 1)
    #sublog = ocel.log[ocel.log["event_variant"]<= last_filtered_variant].copy()
    new_log = OCEL(sublog, object_types=ocel.object_types, execution_extraction=ocel._execution_extraction, leading_object_type=ocel._leading_type)
    #remove all object references of irrelevant objects
    new_log.remove_object_references(rel_obs)
    return new_log