from dataclasses import dataclass
import pandas as pd


@dataclass
class ObjectChangeTable:
    eog: pd.DataFrame