import ast
import pickle
import random
import timeit
from functools import partial
from pathlib import Path

import pandas as pd

from ocpa.objects.log.converter import factory as converter_factory
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.objects.log.variants.obj import (
    Event,
    MetaObjectCentricData,
    Obj,
    ObjectCentricEventLog,
)


def sample_dict(n: int, dy: dict, seed: int = 42) -> dict:
    """only exists for logging purposes"""
    random.seed(seed)
    keys = random.sample(list(dy.keys()), n)
    return {k: dy[k] for k in keys}


base_path = Path("C:/Users/Tim/Development/OCPPM/data/otc_example")

with open(base_path.joinpath("objects_found_in_event_references.pkl"), "rb") as f:
    objects_found_in_event_references = pickle.load(f)
with open(base_path.joinpath("objects_table.pkl"), "rb") as f:
    objects_table: pd.DataFrame = pickle.load(f)
    objects_table["cost2"] = objects_table["cost"] ** 2

df_events = pd.read_csv(base_path.joinpath("events_otc_example.csv"), sep=";")
df_objects = pd.read_csv(base_path.joinpath("objects_otc_example.csv"), sep=";")

# When ocpa.objects.log.converter.factory.apply is called in its context
# (not directly but via an ocel import factory)
# the following has already been performed.
df_events["event_id"] = df_events["event_id"].astype(int)
df_events["event_timestamp"] = pd.to_datetime(df_events["event_timestamp"])
df_events["event_resource"] = df_events["event_resource"].astype("category")
df_events["event_activity"] = df_events["event_activity"].astype("category")
df_events["order"] = df_events["order"].apply(ast.literal_eval)
df_events["item"] = df_events["item"].apply(ast.literal_eval)
df_events["package"] = df_events["package"].apply(ast.literal_eval)

df_objects["cost2"] = df_objects["cost"] ** 2


print(df_events.dtypes)


def load_ocel():
    return converter_factory.apply(
        df_events,
        parameters={"objects_table": df_objects},
        variant=converter_factory.DF_TO_OCEL,
    )


load_ocel_speed = min(timeit.repeat(load_ocel, number=100, repeat=25))
print("Baseline performance: ", load_ocel_speed)

ocel = load_ocel()
