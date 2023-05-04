import pandas as pd
def construct_table(feature_storage, index_list = "all"):
    '''
    Constructs a tabular encoding of the feature_graphs of a feature storage. Each event is transformed into one row
    of the table with the columns being the event's extracted features.

    :param feature_storage: Feature storage to construct a sequential encoding from.
    :type feature_storage: :class:`Feature Storage <ocpa.algo.predictive_monitoring.obj.Feature_Storage>`

    :param index_list: list of indices to be encoded as sequences. Default is "all"
    :type index_list: "all" or list(int)

    :return: List of sequential encodings: Each sequential encoding is a sequence of feature dicts.
    :rtype: list(list(dict))
    '''
    dict_list = []
    for g in feature_storage.feature_graphs:
        if index_list == "all" or g.pexec_id in index_list:
            for node in g.nodes:
                dict_list.append(node.attributes)
    df = pd.DataFrame(dict_list)
    return df