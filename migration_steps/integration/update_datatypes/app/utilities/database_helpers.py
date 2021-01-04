import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")
import helpers

environment = os.environ.get("ENVIRONMENT")
config = helpers.get_config(env=environment)

import logging
from typing import Dict

log = logging.getLogger("root")


def generate_select_string(mapping_details: Dict, schema: str, table_name: str) -> str:
    log.debug(f"Generating select statement for {schema} - {table_name}")
    cols = ", ".join(list(mapping_details.keys()))
    statement = f"SELECT {cols} from {schema}.{table_name};"
    log.log(config.VERBOSE, f"Statement: {statement}")
    return statement


def generate_mapping_table_create(
    schema: str, table_name: str, mapping_columns: Dict
) -> str:
    log.debug(f"Generating mapping table create statement for {table_name}")
    statement = f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} (\n"

    columns = []
    for col, details in mapping_columns.items():
        columns.append(f"{col} {details}")

    statement += ", ".join(columns)

    statement += ");"
    log.log(config.VERBOSE, f"Mapping table create statement: {statement}")
    return statement
