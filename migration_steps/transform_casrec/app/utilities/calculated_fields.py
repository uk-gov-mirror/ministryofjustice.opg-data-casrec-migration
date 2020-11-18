import json
import random
from datetime import datetime

import pandas as pd
import os
import logging

from config import get_config

log = logging.getLogger("root")
environment = os.environ.get("ENVIRONMENT")

config = get_config(env=environment)


def current_date(column_name: str, df: pd.DataFrame) -> pd.DataFrame:
    df[column_name] = datetime.now().strftime("%Y-%m-%d")

    return df
