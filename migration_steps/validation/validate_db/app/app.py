import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from config2 import get_config
from dotenv import load_dotenv
from helpers import log_title
from db_helpers import *
# from entities import client
# from entities import address
import pandas as pd
import logging
import custom_logger
import click

from tabulate import tabulate
from helpers import get_mapping_dict
import json
from typing import Dict, List

sql_path = current_path / "sql"
env_path = current_path / "../../../../.env"
mapping_path = current_path / "../../../shared/mapping_definitions"
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
    log.info(log_title(message="Validation"))

    # log.info("Migration Results")
    #
    # table = [
    #     ['Clients', 1000, 1000, 1000, 1000, 258, 742, 1000, '100%', 0, u'\u2714'],
    #     ['Addresses', 1000, 1000, 1000, 999, 258, 742, 999, '99.9%', 1, u'\u274C']
    # ]
    #
    # headers = ['Entity', 'Rows attempted', 'Transformed OK', 'Integration OK', 'Pre-Migrate', 'Sirius New',
    #            'Sirius Updated', 'Sirius Total', 'Sirius %', 'Exceptions', 'Result']
    #
    # print(tabulate(table, headers=headers, tablefmt="psql"))
    #
    # log.info("Development Progress")
    #
    # table = [
    #     ['Clients', u'\u2714'],
    #     ['Addresses', u'\u2714'],
    #     ['Cases', u'\u2714'],
    #     ['Something Else', u'\u274C'],
    # ]
    #
    # headers = [
    #     'Entity',
    #     'Mapped',
    # ]
    #
    # print(tabulate(table, headers=headers, tablefmt="psql"))


    log.info("Mapping progress report")

    file_path = mapping_path / "summary/mapping_progress_summary.json"

    summary_dict = json.load(open(file_path))

    report_data = []
    for worksheet, worksheet_summary in summary_dict['worksheets'].items():
        report_data.append([worksheet] + list(worksheet_summary.values()))

    headers = ["Casrec Worksheet", "Rows", "Unmapped", "Mapped", "Complete (%)"]
    print(tabulate(report_data, headers, tablefmt="psql"))


    log.info("Migration Validation")
    conn_migration = psycopg2.connect(config.get_db_connection_string("migration"))
    conn_target = psycopg2.connect(config.get_db_connection_string("target"))




if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
