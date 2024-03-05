from dataclasses import dataclass
import pandas as pd
from typing import Dict

@dataclass
class ObjectChangeTable:
    tables: Dict[str,pd.DataFrame]