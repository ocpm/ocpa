import logging
import random
from dataclasses import dataclass, field
from numbers import Number
from typing import Union

import pandas as pd


@dataclass
class Table:
    # __slots__ = (
    #     "variants_dict",
    #     "variants",
    #     "log",
    #     "object_types",
    #     "cases",
    #     "case_objects",
    #     "_log",
    #     "_object_types",
    #     "_object_attributes",
    #     "_numpy_log",
    #     "_column_mapping",
    #     "_mapping",
    #     "_cases",
    #     "_case_objects",
    # )

    def __init__(
        self,
        log: pd.DataFrame,
        parameters: dict,
        object_attributes: Union[pd.DataFrame, dict] = {},
    ):
        self._log = log.copy()
        self._log.set_index("event_id", inplace=True)
        self._log["event_id"] = self._log.index
        self._object_types = parameters["obj_names"]
        self._object_attributes = object_attributes
        # self._event_mapping =  dict(zip(ocel["event_id"], ocel["event_objects"]))
        # clean empty events
        # self._clean_empty_events()
        self.create_efficiency_objects()
        # self._log = self._log[self._log.apply(lambda x: any([len(x[ot]) > 0 for ot in self._object_types]))]

    def _get_log(self) -> pd.DataFrame:
        return self._log

    def _get_object_types(self) -> list[str]:
        return self._object_types

    log: pd.DataFrame = property(_get_log)
    object_types: list[str] = property(_get_object_types)

    def create_efficiency_objects(self):
        self._numpy_log = self._log.to_numpy()
        self._column_mapping = {
            k: v for v, k in enumerate(list(self._log.columns.values))
        }

        self._mapping = {
            c: dict(zip(self._log["event_id"], self._log[c]))
            for c in self._log.columns.values
        }
        if type(self._object_attributes) == pd.DataFrame:
            efficiency_dict = self._object_attributes.set_index("object_id").to_dict()
            efficiency_dict["object_id"] = {
                x: x for x in self._object_attributes["object_id"]
            }  # 2023-06-07 15:23:54 Not sure if this is required, but including this we have the same result as the old code
            self._object_attributes = efficiency_dict
        elif self._object_attributes is None:
            self._object_attributes = {}

    def get_value(self, e_id, attribute):
        return self._mapping[attribute][e_id]

    def get_object_attribute_value(self, o_id, attribute):
        return self._object_attributes[o_id][attribute]

    # Not guaranteed to keep everything consistent, only as quick helpers

    def get_objects_of_variants(self, variants) -> dict:
        obs = {}
        for ot in self.object_types:
            obs[ot] = set()
        for v_id in variants:
            for case_id in self.variants_dict[self.variants[v_id]]:
                for ob in self.case_objects[case_id]:
                    obs[ob[0]].add(ob[1])

        return obs

    def remove_object_references(self, to_keep):
        """Impure (in place) method that removes object references"""
        for ot in self.object_types:
            self.log[ot] = self.log[ot].apply(lambda x: list(set(x) & to_keep[ot]))
        self._clean_empty_events()

    def _clean_empty_events(self):
        self._log = self._log[self._log[self._object_types].astype(bool).any(axis=1)]

    def sample_cases(self, percent: Number):
        index_array = random.sample(
            list(range(0, len(self.cases))), int(len(self.cases) * percent)
        )
        self._cases = [self.cases[i] for i in index_array]
        self._case_objects = [self.case_objects[i] for i in index_array]
