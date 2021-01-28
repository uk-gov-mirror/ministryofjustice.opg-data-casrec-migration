import json
import os
import logging
import sys
from pathlib import Path

import psycopg2
from psycopg2 import errors
import pandas as pd

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../shared")

import db_helpers

completed_tables = []

log = logging.getLogger("root")


def get_columns_query(table, schema):
    return f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{table}';
        """


def remove_unecessary_columns(columns):
    unecessary_field_names = ["method", "sirius_id"]

    unecessary_field_names += [x for x in columns if x[:15] == "transformation_"]

    return [column for column in columns if column not in unecessary_field_names]


def insert_data_into_target(db_config, source_db_engine, table):
    log.info(f"Inserting new data from {db_config['source_schema']} '{table}' table")
    get_cols_query = get_columns_query(table=table, schema=db_config["source_schema"])

    columns = [x[0] for x in source_db_engine.execute(get_cols_query).fetchall()]

    columns = remove_unecessary_columns(columns=columns)

    query = f"""
        SELECT {', '.join(columns)} FROM {db_config["source_schema"]}.{table}
        WHERE method = 'INSERT';
    """

    data_to_insert = pd.read_sql_query(
        sql=query, con=db_config["source_db_connection_string"]
    )

    log.debug(f"Inserting {len(data_to_insert)} rows")

    # special cases
    if table == "addresses":
        log.debug("Reformatting 'address_lines' to json")
        data_to_insert["address_lines"] = data_to_insert["address_lines"].apply(
            json.dumps
        )

    target_connection = psycopg2.connect(db_config["target_db_connection_string"])
    db_helpers.execute_insert(conn=target_connection, df=data_to_insert, table=table)


def update_data_in_target(db_config, source_db_engine, table):
    log.info(
        f"Updating existing data from {db_config['source_schema']} '{table}' table"
    )
    get_cols_query = get_columns_query(table=table, schema=db_config["source_schema"])

    columns = [x[0] for x in source_db_engine.execute(get_cols_query).fetchall()]

    columns = remove_unecessary_columns(columns=columns)

    query = f"""
        SELECT {', '.join(columns)} FROM {db_config["source_schema"]}.{table}
        WHERE method = 'UPDATE';
    """

    data_to_update = pd.read_sql_query(
        sql=query, con=db_config["source_db_connection_string"]
    )
    log.debug(f"Updating {len(data_to_update)} rows")

    # special cases
    if table == "addresses":
        log.debug("Reformatting 'address_lines' to json")
        data_to_update["address_lines"] = data_to_update["address_lines"].apply(
            json.dumps
        )

    target_connection = psycopg2.connect(db_config["target_db_connection_string"])
    db_helpers.execute_update(
        conn=target_connection, df=data_to_update, table=table, pk_col="id"
    )
