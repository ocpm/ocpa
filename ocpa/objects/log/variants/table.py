import time
from dataclasses import dataclass, field
import networkx as nx
import itertools
import random
import pandas as pd
from typing import Dict


@dataclass
class Table:
    def __init__(self, log, parameters, object_attributes=None):
        self._log = log
        self._log["event_id"] = self._log["event_id"].astype(int)
        self._log["event_index"] = self._log["event_id"]
        self._log = self._log.set_index("event_index")
        self._object_types = parameters["obj_names"]
        self._object_attributes = object_attributes
        #self._event_mapping =  dict(zip(ocel["event_id"], ocel["event_objects"]))
        # clean empty events
        # self.clean_empty_events()
        self.create_efficiency_objects()
        #self._log = self._log[self._log.apply(lambda x: any([len(x[ot]) > 0 for ot in self._object_types]))]

    def _get_log(self):
        return self._log

    def _get_object_types(self):
        return self._object_types

    log = property(_get_log)
    object_types = property(_get_object_types)

    def create_efficiency_objects(self):

        self._numpy_log = self._log.to_numpy()
        self._column_mapping = {k: v for v, k in enumerate(
            list(self._log.columns.values))}

        self._mapping = {c: dict(
            zip(self._log["event_id"], self._log[c])) for c in self._log.columns.values}
        if self._object_attributes:
            self._object_attributes = {c: dict(
                zip(self._object_attributes["object_id"], self._object_attributes[c])) for c in self._object_attributes.columns.values}
        else:
            self._object_attributes = {}

    def get_value(self, e_id, attribute):
        return self._mapping[attribute][e_id]

    def get_object_attribute_value(self, o_id, attribute):
        return self._object_attributes[o_id][attribute]

    # Not guaranteed to keep everything consistent, only as quick helpers

    def get_objects_of_variants(self, variants):
        obs = {}
        for ot in self.object_types:
            obs[ot] = set()
        for v_id in variants:
            for case_id in self.variants_dict[self.variants[v_id]]:
                for ob in self.case_objects[case_id]:
                    obs[ob[0]].add(ob[1])

        return obs

    def remove_object_references(self, to_keep):
        # this is in place!
        for ot in self.object_types:
            self.log[ot] = self.log[ot].apply(
                lambda x: list(set(x) & to_keep[ot]))
        self.clean_empty_events()

    def clean_empty_events(self):
        self._log = self._log[self._log[self._object_types].astype(
            bool).any(axis=1)]

    def sample_cases(self, percent):
        index_array = random.sample(
            list(range(0, len(self.cases))), int(len(self.cases)*percent))
        self._cases = [self.cases[i] for i in index_array]
        self._case_objects = [self.case_objects[i] for i in index_array]
