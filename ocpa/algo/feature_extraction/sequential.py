from ocpa.algo.filtering.log import time_filtering
import ocpa.algo.feature_extraction.factory as feature_extraction
import numpy as np
import pandas as pd
import time
def construct_sequence(feature_storage, index_list = "all"):
    if index_list == "all":
        index_list = list(range(0, len(feature_storage.feature_graphs)))
    sequences = []
    for g in [feature_storage.feature_graphs[i] for i in index_list]:
        sequence = []
        #sort nodes on event time (through the event id)
        event_ids = [n.event_id for n in g.nodes]
        event_ids.sort()
        for e_id in event_ids:
            for node in g.nodes:
                if e_id == node.event_id:
                    sequence.append(node.attributes)
        sequences.append(sequence)
    return sequences

def construct_k_dataset(sequences, k, features, target):
    X = []
    y = []
    for s in sequences:
        if len(s) != 0:
            for i in range(k - 1, len(s)):
                seq = []
                for j in range(i - (k - 1), i + 1):
                    seq.append([s[j][feat] for feat in features])
                y.append(s[i][target])
                X.append(seq)
    return X, y