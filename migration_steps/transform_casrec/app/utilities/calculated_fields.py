import json
import random
import pandas as pd
import os
import logging

from config import get_config

log = logging.getLogger("root")
environment = os.environ.get("ENVIRONMENT")

config = get_config(env=environment)


def current_date(original_col: str, final_col: str, df: pd.DataFrame) -> pd.DataFrame:
    df["new"] = pd.datetime.now().strftime("%Y-%m-%d")
    df = df.drop(columns=original_col)
    df = df.rename(columns={"new": final_col})

    return df
