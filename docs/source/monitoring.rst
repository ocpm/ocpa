Object-Centric Predictive Process Monitoring
#####################
OCPA offers extensive support for predictive process monitoring. This comes in form of features extraction, encoding and preprocessing functionality.
Features are extracted based on the true, graph-like structure of object-centric event data. Depending on the use case, users can decide to encode object-centric features in one of three ways:
Tabluer, Sequential or graph. The extracted features can already be normalized and split into training and testing set.

Feature extraction
___________

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    activities = list(set(ocel.log.log["event_activity"].tolist()))
    feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
                  [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities]
    feature_storage = predictive_monitoring.apply(ocel, feature_set, [])

The extracted features come in form of a :class:`Feature Storage <ocpa.algo.feature_extraction.obj.Feature_Storage>`. A feature storage
contains a list of feature graphs. Each feature graph represents one process execution. Each node represents an event. The feature values extracted for events are stored as a dictionary. The feature values for a process execution are, also, stored as a dictionary associated with the feature graph.
Feature functions are predefined (can of course be extended). A funciton is identified with the corresponding string. Parameters are passed as a tuple.

Feature Encoding
___________
The feature storage has an underlying graph structure. OCPA allows the user to transform this graph structure to a sequential or a tabular encoding.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
    from ocpa.algo.predictive_monitoring import tabular, sequential
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    activities = list(set(ocel.log.log["event_activity"].tolist()))
    feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
                  [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities]
    feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
    table = tabular.construct_table(feature_storage)
    sequences = sequential.construct_sequence(feature_storage)

Preprocessing
___________
Since predictive process monitoring is the most common use case of feature extraction and encoding, OCPA allow the user to split and normalize the feature storage for training and testing.
The share of test split is necessary, as well as the state for random splitting.

.. code-block:: python

    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
    from ocpa.algo.predictive_monitoring import tabular

    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    activities = list(set(ocel.log.log["event_activity"].tolist()))
    feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
                  [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities]
    feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
    feature_storage.extract_normalized_train_test_split(0.3, state = 3395)
    train_table = tabular.construct_table(
            feature_storage, index_list=feature_storage.training_indices)
    test_table = tabular.construct_table(
            feature_storage, index_list=feature_storage.test_indices)

Full Example
___________

.. code-block:: python

    from ocpa.util.util import LinearRegression
    from ocpa.util.util import mean_absolute_error
    from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
    from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
    from ocpa.algo.predictive_monitoring import tabular

    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)
    activities = list(set(ocel.log.log["event_activity"].tolist()))
    feature_set = [(predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, ("GDSRCPT",)),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ())] + \
                  [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities]
    feature_storage = predictive_monitoring.apply(ocel, feature_set, [])
    feature_storage.extract_normalized_train_test_split(0.3, state = 3395)
    train_table = tabular.construct_table(
            feature_storage, index_list=feature_storage.training_indices)
    test_table = tabular.construct_table(
            feature_storage, index_list=feature_storage.test_indices)
    y_train, y_test = train_table[feature_set[0]], test_table[feature_set[0]]
    x_train, x_test = train_table.drop(
            feature_set[0], axis=1), test_table.drop(feature_set[0], axis=1)
    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    avg_rem = sum(y_train)/len(y_train)
    print('MAE baseline: ', mean_absolute_error(
        y_test, [avg_rem for elem in y_test]))
    print('MAE: ', mean_absolute_error(y_test, y_pred))
