import logging
import os

import helpers
import pandas as pd

log = logging.getLogger("root")
environment = os.environ.get("ENVIRONMENT")

config = helpers.get_config(env=environment)


def map_lookup_tables(
    lookup_tables: dict, source_data_df: pd.DataFrame
) -> pd.DataFrame:

    for col, details in lookup_tables.items():
        default_value = details["default_value"]
        lookup_dict = helpers.get_lookup_dict(file_name=details["lookup_table"])

        source_data_df[col] = source_data_df[col].map(lookup_dict)

        if default_value:
            source_data_df[col] = source_data_df[col].fillna(default_value)
        else:
            source_data_df[col] = source_data_df[col].fillna("")

    return source_data_df
