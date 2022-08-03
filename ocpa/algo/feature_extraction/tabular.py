import pandas as pd
def construct_table(feature_storage, index_list = "all"):
    if index_list == "all":
        index_list = list(range(0,len(feature_storage.feature_graphs)))
    dict_list = []
    for g in [feature_storage.feature_graphs[i] for i in index_list]:
        for node in g.nodes:
            dict_list.append(node.attributes)
    df = pd.DataFrame(dict_list)
    return df