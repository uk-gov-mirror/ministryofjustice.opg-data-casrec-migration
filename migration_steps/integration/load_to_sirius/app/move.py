import json
import os
import logging
import sys
from pathlib import Path

import psycopg2
from psycopg2 import errors
import pandas as pd

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

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


def get_data_to_insert(db_config, source_db_engine, target_db_engine):

    path = f"{os.path.dirname(__file__)}/tables.json"

    with open(path) as tables_json:
        tables_list = json.load(tables_json)

    for i, table in enumerate(tables_list):
        log.info(f"Getting data to insert from {db_config['source_schema']}")

        log.debug(f"This is table number {i+1}")

        get_cols_query = get_columns_query(
            table=table, schema=db_config["source_schema"]
        )

        columns = [x[0] for x in source_db_engine.execute(get_cols_query).fetchall()]

        columns = remove_unecessary_columns(columns=columns)

        query = f"""
            SELECT {', '.join(columns)} FROM {db_config["source_schema"]}.{table}
            WHERE method = 'INSERT';
        """

        data_to_insert = pd.read_sql_query(
            sql=query, con=db_config["source_db_connection_string"]
        )

        # special cases
        if table == "addresses":
            data_to_insert["address_lines"] = data_to_insert["address_lines"].apply(
                json.dumps
            )

        target_connection = psycopg2.connect(db_config["target_db_connection_string"])
        db_helpers.execute_insert(
            conn=target_connection, df=data_to_insert, table=table
        )

        # insert_statement = create_insert_statement(table_name=table, df=data_to_insert, db_config=db_config)
        #
        #
        #
        # target_db_engine.execute(insert_statement)


def create_insert_statement(table_name, df, db_config):
    columns = [x for x in df.columns.values]
    insert_statement = f"""INSERT INTO {table_name} ("""
    for i, col in enumerate(columns):
        insert_statement += f'"{col}"'
        if i + 1 < len(columns):
            insert_statement += ","

    insert_statement += ") \n VALUES \n"

    for i, row in enumerate(df.values.tolist()):

        row = [str(x) for x in row]
        row = [
            str(
                x.replace("'", "''")
                .replace("NaT", "")
                .replace("nan", "")
                .replace("None", "")
                .replace("&", "and")
                .replace(";", "-")
                .replace("%", "percent")
            )
            for x in row
        ]
        row = [f"'{str(x)}'" if str(x) != "" else "NULL" for x in row]

        single_row = ", ".join(row)

        insert_statement += f"({single_row})"

        if i + 1 < len(df):
            insert_statement += ",\n"
        else:
            insert_statement += ";\n\n\n"
    return insert_statement
