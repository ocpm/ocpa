def construct_sequence(feature_storage, index_list = "all"):
    '''
    Constructs a sequential respresentation of the feature_graphs of a feature storage.

    :param feature_storage: Feature storage to construct a sequential encoding from.
    :type feature_storage: :class:`Feature Storage <ocpa.algo.predictive_monitoring.obj.Feature_Storage>`

    :param index_list: list of indices to be encoded as sequences. Default is "all"
    :type index_list: "all" or list(int)

    :return: List of sequential encodings: Each sequential encoding is a sequence of feature dicts.
    :rtype: list(list(dict))

    '''
    sequences = []
    for g in feature_storage.feature_graphs:
        if index_list == "all" or g.pexec_id in index_list:
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