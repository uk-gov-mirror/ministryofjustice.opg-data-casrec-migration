import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../shared")
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import click
import time
import logging
import custom_logger
import config2
from db_helpers import create_schema

env_path = current_path / "../../.env"
load_dotenv(dotenv_path=env_path)
environment = os.environ.get("ENVIRONMENT")
config = config2.get_config(env=environment)

config.custom_log_level()
verbosity_levels = config.verbosity_levels
log = logging.getLogger("root")
log.addHandler(custom_logger.MyHandler())

casrec_engine = create_engine(config.get_db_connection_string("migration"))
sirius_engine = create_engine(config.get_db_connection_string("target"))
casrec_schema = "audit"
list_of_tables = []


def copy_table(engine_from, engine_to, schema_from, schema_to, table_from, table_to):
    select_table_statement = f"""
    SELECT *
    FROM {schema_from}.{table_from};
    """

    df = pd.read_sql(select_table_statement, engine_from)
    df.to_sql(
        name=table_to,
        schema=schema_to,
        con=engine_to,
        if_exists="replace",
        index=False,
        chunksize=10000,
    )


def get_update_rows_statement(audit_value, schema, table, pk):
    if audit_value == "current":
        new_audit_value = "new"
    elif audit_value == "previous":
        new_audit_value = "deleted"
    else:
        log.error("Incorrect audit value")
        exit(1)

    update_rows_statement = f"""
        update {schema}.{table}_audit set audit_value = '{new_audit_value}'
        where {pk} in
        (select mt.{pk}
        from {schema}.{table}_audit mt
        inner join
        (select {pk}, count(*)
        from {schema}.{table}_audit
        group by {pk}
        having count(*) = 1) as st
        on mt.{pk} = st.{pk}
        where mt.audit_value = '{audit_value}')
    """
    return update_rows_statement


def get_change_statement(schema, table, from_src):
    select_change = f"""
        SELECT *
        FROM {schema}.{table}_{'before' if from_src else 'after'}
        EXCEPT
        SELECT *
        FROM {schema}.{table}_{'after' if from_src else 'before'};
        """
    return select_change


def diff_old_new(engine, schema, table, pk):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    df_from = pd.read_sql(get_change_statement(schema, table, True), engine)
    df_from.insert(loc=0, column="audit_value", value="previous")
    df_from.insert(loc=0, column="mig_timestamp", value=ts)

    df_to = pd.read_sql(get_change_statement(schema, table, False), engine)
    df_to.insert(loc=0, column="audit_value", value="current")
    df_to.insert(loc=0, column="mig_timestamp", value=ts)

    df_combined = df_from.append(df_to)
    df_combined.to_sql(
        name=table,
        schema=schema,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=10000,
    )

    response = engine.execute(get_update_rows_statement("previous", schema, table, pk))
    if response.rowcount > 0:
        log.info(f"Updated {table} statuses for deleted rows")
    response = engine.execute(get_update_rows_statement("current", schema, table, pk))
    if response.rowcount > 0:
        log.info(f"Updated {table} statuses for new rows")


def clear_up(engine, schema, table):
    for direction in ["before", "after"]:
        drop_statement = f"DROP TABLE {schema}.{table}_{direction}"
        response = engine.execute(drop_statement)
        if response.rowcount > 0:
            log.debug(f"Dropped {schema}.{table}_{direction}")


@click.command()
@click.option("-c", "--command", default="before")
@click.option("-v", "--verbose", count=True)
def main(command, verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
        log.info(f"{verbosity_levels[verbose]} logging enabled")
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")
        log.info(f"INFO logging enabled")

    create_schema(log, casrec_engine, casrec_schema)

    table = "persons"

    if command == "before":
        copy_table(
            sirius_engine,
            casrec_engine,
            "public",
            casrec_schema,
            table,
            f"{table}_before",
        )
        log.info(f"Copied {table} before update to {table}_before")
    elif command == "after":
        copy_table(
            sirius_engine,
            casrec_engine,
            "public",
            casrec_schema,
            table,
            f"{table}_after",
        )
        log.info(f"Copied {table} after update to {table}_after")
        diff_old_new(casrec_engine, casrec_schema, table, "id")
        clear_up(casrec_engine, casrec_schema, table)
    else:
        log.error(f"ERROR Invalid command")
        exit(1)


if __name__ == "__main__":
    main()
