import ocpa.algo.event_correlation.weakly_connected_components as variant_extraction
import ocpa.objects.eog.retrieval.log as event_object_graph_extractor
from ocpa.objects.ocel.obj import OCEL


def filter_infrequent_traces(ocel, threshold):
    v_freq_acc = [sum(ocel.variant_frequency[0:i+1]) for i in range(0,len(ocel.variant_frequency))]
    last_filtered_variant = len(v_freq_acc)-1
    for i in range(0,len(v_freq_acc)):
        if v_freq_acc[i] > threshold:
            last_filtered_variant = i
            break
    sublog = ocel.log[ocel.log["event_variant"]<= last_filtered_variant].copy()
    return OCEL(sublog, object_types=ocel.object_types)