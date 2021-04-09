import os
import sys
from pathlib import Path


current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../shared")

import logging
import time
import click
from sqlalchemy import create_engine
import custom_logger
from helpers import log_title
import helpers
from decorators import timer, mem_tracker

from dotenv import load_dotenv

from entities import clients


# set config
current_path = Path(os.path.dirname(os.path.realpath(__file__)))
env_path = current_path / "../../.env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")


config = helpers.get_config(env=environment)

# logging
log = logging.getLogger("root")
custom_logger.setup_logging(env=environment)


# database
db_config = {
    "db_connection_string": config.get_db_connection_string("migration"),
    "source_schema": config.schemas["pre_transform"],
    "target_schema": config.schemas["post_transform"],
}

allowed_entities = [k for k, v in config.ENABLED_ENTITIES.items() if v is True]


@click.command()
@click.option(
    "--clear",
    prompt=False,
    default=False,
    help="Clear existing database tables: True or False",
)
@click.option(
    "--include_tests",
    help="Run data tests after performing the transformations",
    default=False,
)
@click.option(
    "--chunk_size",
    prompt=False,
    type=int,
    help="Defaults to 10,000 but can be changed for dev",
    default=10000,
)
@mem_tracker
@timer
def main(clear, include_tests, chunk_size):

    log.info(log_title(message="Migration Step: Transform Casrec Data"))
    log.info(
        log_title(
            message=f"Source: {db_config['source_schema']} Target: {db_config['target_schema']}"
        )
    )
    log.info(
        log_title(
            message=f"Enabled entities: {', '.join(k for k, v in config.ENABLED_ENTITIES.items() if v is True)}"
        )
    )
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")
    version_details = helpers.get_json_version()
    log.info(
        f"Using JSON def version '{version_details['version_id']}' last updated {version_details['last_modified']}"
    )
    clients.runner(db_config=db_config)


if __name__ == "__main__":
    t = time.process_time()

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
