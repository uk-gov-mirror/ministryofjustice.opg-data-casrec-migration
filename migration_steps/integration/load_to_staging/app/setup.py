import json
import os
import sys
import logging

import psycopg2
from psycopg2 import errors

log = logging.getLogger("root")


def insert_base_data(db_config, db_engine):
    log.info("inserting base data")

    # insert default user into assignees
    base_data = {
        "assignees": f"""
        INSERT INTO {db_config['target_schema']}.assignees(id, name, type)
            VALUES
            (10, 'casrec migration', 'default'),
--             (1, 'casrec migration', 'default');
            (2, 'casrec migration', 'default');
        """,
        "bond_providers": f"""
        insert into {db_config['target_schema']}.bond_providers (id, name, oneoffvalue, telephonenumber, emailaddress, webaddress, uid)
            values
                (1,'Howden',21000.00,null,null,'https://www.howdendeputybonds.co.uk','HOWDEN'),
                (2,'Deputy Bond Services (DBS)',21000.00,null,null,'https://www.deputybondservices.co.uk','DBS'),
                (3,'Marsh',16000.00,null,null,null,'MARSH'),
                (185,'Howden',21000.00,null,null,'https://www.howdendeputybonds.co.uk','HOWDEN_dev'),
                (186,'Deputy Bond Services (DBS)',21000.00,null,null,'https://www.deputybondservices.co.uk','DBS_dev'),
                (187,'Marsh',16000.00,null,null,null,'MARSH_dev'),
                (43745,'OTHER',null,null,null,null,'OTHER_dev');
        """,
        "casrec_extra_data": f"""
            CREATE TABLE IF NOT EXISTS {db_config['target_schema']}.casrec_extra_data (
                id serial primary key,
                entity text,
                sirius_table text,
                sirius_pk_column text,
                sirius_pk int,
                details json
            )
        """,
    }
    for name, statement in base_data.items():

        try:
            with db_engine.begin() as conn:
                conn.execute(statement)

        except Exception as e:
            log.error(
                f"There was an error inserting the {name} data into {db_config['target_schema']}"
            )
            log.debug(e)
            os._exit(1)
