import json
import os
import logging
import sys
from pathlib import Path

import numpy as np
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
    unecessary_field_names = ["method"]

    return [column for column in columns if column not in unecessary_field_names]


def insert_data_into_target(db_config, source_db_engine, table, pk):
    log.info(f"Inserting new data from {db_config['source_schema']} '{table}' table")
    get_cols_query = get_columns_query(table=table, schema=db_config["source_schema"])

    columns = [x[0] for x in source_db_engine.execute(get_cols_query).fetchall()]

    columns = remove_unecessary_columns(columns=columns)

    chunk_size = 10000
    offset = 0
    while True:
        query = f"""
            SELECT {', '.join(columns)}
            FROM {db_config["source_schema"]}.{table}
            WHERE method = 'INSERT'
            ORDER BY {pk}
            LIMIT {chunk_size} OFFSET {offset};;
        """

        data_to_insert = pd.read_sql_query(
            sql=query, con=db_config["source_db_connection_string"]
        )
        for col in columns:
            data_to_insert[col] = (
                data_to_insert[col]
                .astype(str)
                .replace({"NaT": None, "None": None, "NaN": None})
            )

        # special cases
        if table == "addresses":
            log.debug("Reformatting 'address_lines' to json")
            data_to_insert["address_lines"] = data_to_insert["address_lines"].apply(
                json.dumps
            )

        log.debug(f"Inserting {len(data_to_insert)} rows")

        target_connection = psycopg2.connect(db_config["target_db_connection_string"])
        db_helpers.execute_insert(
            conn=target_connection, df=data_to_insert, table=table
        )

        offset += chunk_size
        print(f"doing offset {offset} for table {table}")
        if len(data_to_insert) < chunk_size:
            break


def update_data_in_target(db_config, source_db_engine, table, pk):
    log.info(
        f"Updating existing data from {db_config['source_schema']} '{table}' table"
    )
    get_cols_query = get_columns_query(table=table, schema=db_config["source_schema"])

    columns = [x[0] for x in source_db_engine.execute(get_cols_query).fetchall()]

    columns = remove_unecessary_columns(columns=columns)

    chunk_size = 10000
    offset = 0
    while True:
        query = f"""
            SELECT {', '.join(columns)} FROM {db_config["source_schema"]}.{table}
            WHERE method = 'UPDATE'
            ORDER BY {pk}
            LIMIT {chunk_size} OFFSET {offset};
        """

        data_to_update = pd.read_sql_query(
            sql=query, con=db_config["source_db_connection_string"]
        )
        for col in columns:
            data_to_update[col] = (
                data_to_update[col]
                .astype(str)
                .replace({"NaT": None, "None": None, "NaN": None})
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

        offset += chunk_size
        print(f"doing offset for update: {offset} for table {table}")
        if len(data_to_update) < chunk_size:
            break
