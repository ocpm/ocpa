from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple, Union
import datetime


@dataclass
class TimeWindow(object):
    start: datetime.datetime
    end: datetime.datetime
