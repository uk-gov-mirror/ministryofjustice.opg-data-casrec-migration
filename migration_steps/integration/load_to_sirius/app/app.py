import json
import sys
import os
from pathlib import Path

from move import insert_data_into_target, update_data_in_target

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import logging
import time
import click
from sqlalchemy import create_engine
import custom_logger
from helpers import log_title
import config2
from dotenv import load_dotenv


# set config
current_path = Path(os.path.dirname(os.path.realpath(__file__)))
env_path = current_path / "../../.env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = config2.get_config(env=environment)

# logging
# custom_logger.custom_log_level(levels=config.custom_log_levels)
config.custom_log_level()
verbosity_levels = config.verbosity_levels
log = logging.getLogger("root")
log.addHandler(custom_logger.MyHandler())

# database
db_config = {
    "source_db_connection_string": config.get_db_connection_string("migration"),
    "target_db_connection_string": config.get_db_connection_string("target"),
    "source_schema": config.schemas["pre_migration"],
    "target_schema": config.schemas["public"],
}
source_db_engine = create_engine(db_config["source_db_connection_string"])
target_db_engine = create_engine(db_config["target_db_connection_string"])


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
        log.info(f"{verbosity_levels[verbose]} logging enabled")
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")
        log.info(f"INFO logging enabled")

    log.info(log_title(message="Integration Step: Load to Staging"))
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    path = f"{os.path.dirname(__file__)}/tables.json"

    with open(path) as tables_json:
        tables_list = json.load(tables_json)

    for i, table in enumerate(tables_list):
        log.debug(f"This is table number {i + 1} of {len(tables_list)}")

        insert_data_into_target(
            db_config=db_config, source_db_engine=source_db_engine, table=table
        )
        update_data_in_target(
            db_config=db_config, source_db_engine=source_db_engine, table=table
        )


if __name__ == "__main__":
    t = time.process_time()

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
