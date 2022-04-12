from ocpa.algo.filtering.log import time_filtering
import ocpa.algo.feature_extraction.factory as feature_extraction
import numpy as np
import pandas as pd
import time
def construct_table(feature_storage):
    features = feature_storage.event_features
    df = pd.DataFrame(columns=features)
    print(df)
    for g in feature_storage.feature_graphs:
        for node in g.nodes:
            #print(node.attributes)
            df = df.append(node.attributes, ignore_index = True)
    print(df)
    return df