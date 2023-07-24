from dataclasses import dataclass
import datetime
import numpy as np
import statistics


@dataclass
class TimeWindow(object):
    start: datetime.datetime
    end: datetime.datetime

import json

def merge_json(file1, file2):
    with open(file1, 'r') as f:
        data1 = json.load(f)
    
    with open(file2, 'r') as f:
        data2 = json.load(f)
    
    # merge 'ocel:global-log'
    merged_global_log = data1['ocel:global-log']
    for key in ['ocel:object-types', 'ocel:attribute-names']:
        merged_global_log[key] = list(set(data1['ocel:global-log'][key] + data2['ocel:global-log'][key]))

    # merge 'ocel:events'
    merged_events = {**data1['ocel:events'], **data2['ocel:events']}

    # merge 'ocel:objects'
    merged_objects = {**data1['ocel:objects'], **data2['ocel:objects']}

    # merge 'ocel:global-event'
    merged_global_event = {**data1['ocel:global-event'], **data2['ocel:global-event']}

    # merge 'ocel:global-object'
    merged_global_object = {**data1['ocel:global-object'], **data2['ocel:global-object']}

    merged_data = {
        'ocel:global-event': merged_global_event,
        'ocel:global-object': merged_global_object,
        'ocel:global-log': merged_global_log,
        'ocel:events': merged_events,
        'ocel:objects': merged_objects,
    }

    with open('merged.json', 'w') as f:
        json.dump(merged_data, f)

    return merged_data

class StandardScaler:
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        return self

    def transform(self, X):
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def inverse_transform(self, X):
        return X * self.scale_ + self.mean_
    
class LinearRegression:
    def __init__(self):
        self.coefficients = None

    def fit(self, X, y):
        # Add a column of ones to X for the intercept term
        X = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)

        # Calculate the coefficients using the normal equation
        X_transpose_X = np.dot(X.T, X)
        X_transpose_y = np.dot(X.T, y)
        self.coefficients = np.linalg.solve(X_transpose_X, X_transpose_y)

    def predict(self, X):
        # Add a column of ones to X for the intercept term
        X = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)

        # Calculate the predicted values
        y_pred = np.dot(X, self.coefficients)
        return y_pred

def mean_absolute_error(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mae = np.mean(np.abs(y_true - y_pred))
    return mae


AGG_MAP = {
    'avg': statistics.mean,
    'med': statistics.median,
    'std': statistics.stdev,
    'sum': sum,
    'min': min,
    'max': max
}
