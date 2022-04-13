from ocpa.algo.filtering.log import time_filtering
import ocpa.algo.feature_extraction.factory as feature_extraction
import numpy as np
import pandas as pd
import time
def construct_sequence(feature_storage):
    sequences = []
    for g in feature_storage.feature_graphs:
        sequence = []
        for node in g.nodes:
            sequence.append(node.attributes)
        sequences.append(sequence)
    return sequences