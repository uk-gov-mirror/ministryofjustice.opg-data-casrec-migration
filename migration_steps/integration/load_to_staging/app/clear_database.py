import json
import logging
import os

import psycopg2

log = logging.getLogger("root")


def empty_target_tables(db_config, db_engine):
    path = f"{os.path.dirname(__file__)}/tables.json"
    log.info(f"path: {path}")

    with open(path) as tables_json:
        tables_list = json.load(tables_json)

    tables_list.reverse()

    tables_list.append("assignees")

    for i, table in enumerate(tables_list):
        log.debug(f"Clearing data from {table} in {db_config['target_schema']}")

        statement = f"""
        DELETE FROM {db_config['target_schema']}.{table} CASCADE;
        """

        try:
            db_engine.execute(statement)
        except Exception as e:
            log.error(
                f"There was an error clearing {table} in {db_config['target_schema']}"
            )
            log.debug(e)
            break
