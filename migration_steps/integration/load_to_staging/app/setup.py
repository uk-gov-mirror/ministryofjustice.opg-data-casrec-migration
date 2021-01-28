import json
import os
import logging

import psycopg2
from psycopg2 import errors

log = logging.getLogger("root")


def insert_base_data(db_config, db_engine):

    # insert default user into assignees
    statement = f"""
    INSERT INTO {db_config['target_schema']}.assignees(id, name, type) VALUES (10, 'casrec migration', 'default');
    """

    try:
        db_engine.execute(statement)
    except Exception as e:
        log.error(
            f"There was an error inserting the setup data into {db_config['target_schema']}"
        )
        log.debug(e)
