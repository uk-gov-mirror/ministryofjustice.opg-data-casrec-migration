import os
import sys
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
from sqlalchemy import create_engine
from config import get_config
from dotenv import load_dotenv
from helpers import log_title
import logging
import custom_logger
import click

# path vars
env_path = current_path / "../../../../.env"
load_dotenv(dotenv_path=env_path)

# env vars
db = os.environ.get("SIRIUS_DB_NAME")
environment = os.environ.get("ENVIRONMENT")
ci = os.getenv("CI")
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


def reindex_db(engine, db):
    reindex_db_statement = f"""
        REINDEX DATABASE {db};
    """
    engine.execute(reindex_db_statement)


def update_statistics_db(engine, db):
    update_stats_statement = f"""
        REINDEX DATABASE {db};
    """
    engine.execute(update_stats_statement)


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose):
    set_logging_level(verbose)
    log.info(log_title(message="Prepare Target"))

    log.info("Perform Post Migration DB Tasks")
    db_conn_string = config.get_db_connection_string("target")
    engine = create_engine(db_conn_string, isolation_level="AUTOCOMMIT")

    log.info("Reindex target DB...\n")
    reindex_db(engine, db)

    log.info("Update stats on target DB...\n")
    update_statistics_db(engine, db)


if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
