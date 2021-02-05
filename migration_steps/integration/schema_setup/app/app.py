import os
import sys
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from config import get_config
from dotenv import load_dotenv
from db_helpers import *
from helpers import log_title
import logging
import custom_logger
import click

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
    log.info(log_title(message="Integration"))

    log.info("Create an integration schema for use with this step")
    copy_schema(
        log=log,
        sql_path=shared_sql_path,
        from_config=config.db_config["migration"],
        from_schema=config.schemas["post_transform"],
        to_config=config.db_config["migration"],
        to_schema=config.schemas["integration"],
    )

    log.info("Modify new schema")
    conn = psycopg2.connect(config.get_db_connection_string("migration"))
    execute_generated_sql(
        local_sql_path,
        "sirius_id_cols.template.sql",
        "{schema}",
        config.schemas["integration"],
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
