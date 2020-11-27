import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from config2 import get_config
from dotenv import load_dotenv
from db_helpers import *
import logging
import custom_logger
import click

import sh
import fileinput

env_path = current_path / "../../../../.env"
local_sql_path = current_path / "sql"
shared_sql_path = current_path / "../../../shared/sql"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)

# logging
log = logging.getLogger("root")
log.addHandler(custom_logger.MyHandler())
config.custom_log_level()
verbosity_levels = config.verbosity_levels


def set_logging_level(verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose):
    set_logging_level(verbose)

    log.info("Create an integration schema for use with this step")
    dbconfig = config.db_config["migration"]
    schema_dump = shared_sql_path/'schemas'/str(config.schemas["post_transform"] + '.sql')

    log.info("Dump transform schema")
    os.environ["PGPASSWORD"] = dbconfig["password"]
    sh.pg_dump(
        '-U', dbconfig["user"],
        '-n', config.schemas["post_transform"],
        '-h', dbconfig["host"],
        '-p', dbconfig["port"],
        dbconfig["name"],
        _out=str(schema_dump)
    )

    log.info("Modify schema")
    with fileinput.FileInput(str(schema_dump), inplace=True) as file:
        for line in file:
            print(line.replace(
                config.schemas["post_transform"],
                config.schemas["integration"]),
                end='')
    with fileinput.FileInput(schema_dump, inplace=True) as file:
        for line in file:
            print(line.replace(
                'CREATE SCHEMA ' + config.schemas["integration"],
                f'DROP SCHEMA IF EXISTS {config.schemas["integration"]} CASCADE; CREATE SCHEMA {config.schemas["integration"]}'),
                end='')

    log.info("Import new schema")
    schemafile = open(schema_dump, 'r')
    sh.psql(
        '-U', dbconfig["user"],
        '-h', dbconfig["host"],
        '-p', dbconfig["port"],
        dbconfig["name"],
        _in=schemafile
    )

    log.info("Modify new schema")
    conn = psycopg2.connect(config.get_db_connection_string("migration"))
    execute_generated_sql(
        local_sql_path,
        "sirius_id_cols.template.sql",
        "{schema}",
        config.schemas['integration'],
        conn,
    )
    conn.close()


if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    if environment in ("local", "development"):
        main()
    else:
        log.warning("Skipping step not designed to run on environment %s", environment)

    print(f"Total time: {round(time.process_time() - t, 2)}")
