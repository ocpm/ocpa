import ocpa.algo.event_correlation.weakly_connected_components as variant_extraction
import ocpa.objects.eog.retrieval.log as event_object_graph_extractor
def filter_infrequent_traces(ocel, threshold, v_freq = None):
    if v_freq == None:
        EOG = event_object_graph_extractor.from_ocel(ocel)
        ocel, variants, v_freq = variant_extraction.from_eog(EOG, ocel) 
    v_freq_acc = [sum(v_freq[0:i+1]) for i in range(0,len(v_freq))]
    last_filtered_variant = len(v_freq_acc)-1
    for i in range(0,len(v_freq_acc)):
        if v_freq_acc[i] > threshold:
            last_filtered_variant = i
            break
    sublog = ocel[ocel["event_variant"]<= last_filtered_variant]
    return sublog