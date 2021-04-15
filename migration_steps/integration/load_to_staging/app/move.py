import json
import os
import sys
import logging

import psycopg2
from psycopg2 import errors

log = logging.getLogger("root")


completed_tables = []


def get_columns_query(table, schema):
    return f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{table}';
        """


def add_missing_columns_query(table, schema, columns):

    query = f"ALTER TABLE {schema}.{table} "
    for i, col in enumerate(columns):
        query += f"ADD COLUMN IF NOT EXISTS {col} TEXT"
        if i + 1 < len(columns):
            query += ", "
    query += ";"

    return query


def generate_inserts(db_config, db_engine, tables):

    tables_list = tables
    extra_cols_to_move_to_staging = ["method"]

    for i, (table, details) in enumerate(tables_list.items()):

        log.info(f"Inserting {table} into {db_config['target_schema']}")

        log.debug(f"This is table number {i+1}")

        try:
            target_table = details["pk_table"]
        except KeyError:
            target_table = table

        get_source_cols_query = get_columns_query(
            table=table, schema=db_config["source_schema"]
        )
        get_target_cols_query = get_columns_query(
            table=target_table, schema=db_config["target_schema"]
        )

        source_columns = [
            x[0] for x in db_engine.execute(get_source_cols_query).fetchall()
        ]
        target_columns = [
            x[0] for x in db_engine.execute(get_target_cols_query).fetchall()
        ]

        cols_to_move = list(
            set(
                [x for x in source_columns if x in target_columns]
                + extra_cols_to_move_to_staging
            )
        )
        print(f"cols_to_move: {cols_to_move}")

        columns_missing_from_target = extra_cols_to_move_to_staging

        if len(columns_missing_from_target) > 0:
            alter_target_query = add_missing_columns_query(
                table=target_table,
                schema=db_config["target_schema"],
                columns=columns_missing_from_target,
            )

            db_engine.execute(alter_target_query)

        query = f"""
        INSERT INTO {db_config["target_schema"]}.{target_table} ({', '.join(cols_to_move)})
        SELECT {', '.join(cols_to_move)} FROM {db_config["source_schema"]}.{table};
        """
        print(f"query: {query}")

        try:
            with db_engine.begin() as conn:
                conn.execute(query)

            global completed_tables
            completed_tables.append(table)
            log.info(
                f"{len(completed_tables)}/{len(tables_list)} tables have been completed"
            )
            log.debug(f"Completed tables: {', '.join(completed_tables)}")
            log.debug(
                f"Not completed tables: {', '.join(list(set(tables_list) - set(completed_tables)))}"
            )
        except Exception as e:
            log.error(
                f"There was an error inserting {table} into {db_config['target_schema']}"
            )
            log.debug(e)
            os._exit(1)
