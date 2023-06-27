from dataclasses import dataclass
import datetime


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

