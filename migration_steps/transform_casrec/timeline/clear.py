import logging

import datetime
import json
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../shared")
from helpers import get_timeline_dict


log = logging.getLogger("root")


def clear_tables(db_config, files):
    for timeline_file_name in files:
        timeline_dict = get_timeline_dict(file_name=timeline_file_name)
        timeline_table_name = (
            f"timeline_event_{timeline_dict['entity']}_{timeline_dict['sirius_table']}"
        )

        target_db_engine = create_engine(db_config["db_connection_string"])

        try:

            with target_db_engine.begin() as conn:

                conn.execute(
                    f"DROP TABLE IF EXISTS {db_config['target_schema']}.{timeline_table_name};"
                )
                log.debug(f"dropped table '{timeline_table_name}'")

        except Exception as e:
            log.error(f"TERRIBLE ERROROR dropping table {timeline_table_name}")
            print(f"e: {e}")
