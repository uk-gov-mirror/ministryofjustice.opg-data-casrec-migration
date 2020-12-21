import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from config2 import get_config
from dotenv import load_dotenv
from helpers import log_title, get_all_mapped_fields
from db_helpers import *
import logging
import custom_logger
import click

from tabulate import tabulate
import json
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

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

mappings_to_run = [
    "client_persons",
    # "client_addresses",
    # "client_phonenumbers",
    # "cases",
    # "person_caseitem"
]

indent = "    "


def set_logging_level(verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")


def mapping_report():
    log.info("Mapping progress report")

    file_path = mapping_path / "summary/mapping_progress_summary.json"
    summary_dict = json.load(open(file_path))

    report_data = []
    for worksheet, worksheet_summary in summary_dict['worksheets'].items():
        report_data.append([worksheet] + list(worksheet_summary.values()))

    headers = ["Casrec Worksheet", "Rows", "Unmapped", "Mapped", "Complete (%)"]
    print(tabulate(report_data, headers, tablefmt="psql"))


def get_sirius_table(mapping):
    mapping_name_to_table = {
        "client_persons": "persons",
        "client_addresses": "addresses",
        "client_phonenumbers": "phonenumbers"
    }
    return mapping_name_to_table.get(mapping, mapping)


def get_exception_table(mapping):
    return f"casrec_migration_exceptions_{mapping}"


def get_map_dict(mapping):
    map_dict = json.load(open(mapping_path / f"{mapping}_mapping.json"))
    return {k: v for k, v in map_dict.items() if v['mapping_status']['is_complete'] and v['sirius_details']['is_pk'] != True}


def build_exception_tables(sql_lines):
    #drop all possible exception tables from last run
    for mapfile in get_all_mapped_fields().keys():
        sql_lines.append(f"DROP TABLE IF EXISTS {get_exception_table(mapfile)};\n")

    sql_lines.append("\n\n")

    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        map_dict = get_map_dict(mapping)
        sql_lines.append(f"CREATE TABLE {exception_table_name}(\n")
        separator = ',\n'
        cols = separator.join([f"{indent}{sirius_col} text default NULL" for sirius_col in map_dict.keys()])
        sql_lines.append(cols)
        sql_lines.append("\n);\n\n")


def format_calculated_value(mapping):
    callables = {
        "current_date": "'" + datetime.now().strftime("%Y-%m-%d") + "'" #just do today's date
    }
    return callables.get(mapping["transform_casrec"]["calculated"])


def format_default_value(mapping):
    default_value = mapping["transform_casrec"]["default_value"]
    if mapping["sirius_details"]["data_type"] in ["date", "datetime", "str"]:
        default_value = f"'{default_value}'"
    return default_value


def casrec_col_sql(mapping, col):
    if mapping["sirius_details"]["data_type"] in ["date", "datetime"]:
        col_sql = f"CAST(NULLIF(TRIM({col}), '') AS DATE)"
    elif mapping["sirius_details"]["data_type"] in ["bool", "int"]:
        col_sql = col
    else:
        col_sql = f'NULLIF(TRIM({col}), \'\')'

    return col_sql


def build_validation_statements(sql_lines):
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        sirius_table_name = get_sirius_table(mapping)
        map_dict = get_map_dict(mapping)

        casrec_cols = []
        casrec_tables = []
        for k, v in map_dict.items():
            if v["transform_casrec"]["casrec_table"]:
                casrec_col_table = v["transform_casrec"]["casrec_table"].lower()
                casrec_col_name = v["transform_casrec"]["casrec_column_name"]
                casrec_tables.append(config.schemas['casrec_csv'] + '.' + casrec_col_table)
                col = f'{casrec_col_table}."{casrec_col_name}"'
            elif '' != v["transform_casrec"]["default_value"]:
                col = format_default_value(v)
            elif '' != v["transform_casrec"]["calculated"]:
                col = format_calculated_value(v)
            casrec_cols.append(
                f"{indent}{indent}{indent}{casrec_col_sql(v, col)} AS {k}"
            )

        separator = ',\n'
        casrec_cols = separator.join(casrec_cols)
        sirius_cols = separator.join([f"{indent}{indent}{indent}{s} AS {s}" for s in map_dict.keys()])

        separator = ','
        casrec_tables = separator.join(set(casrec_tables))

        sql_lines.append(f"INSERT INTO {exception_table_name}(\n")
        # casrec half
        sql_lines.append(f"{indent}SELECT * FROM(\n")
        sql_lines.append(f"{indent}{indent}SELECT DISTINCT\n")
        sql_lines.append(f"{casrec_cols}\n")
        sql_lines.append(f"{indent}{indent}FROM {casrec_tables}\n")
        sql_lines.append(f"{indent}{indent}ORDER BY caserecnumber ASC\n")
        # sql_lines.append(f"{indent}{indent}LIMIT 10\n")
        sql_lines.append(f"{indent}) as csv_data\n")
        sql_lines.append(f"{indent}EXCEPT\n")
        # sirius half
        sql_lines.append(f"{indent}SELECT * FROM(\n")
        sql_lines.append(f"{indent}{indent}SELECT DISTINCT\n")
        sql_lines.append(sirius_cols + "\n")
        sql_lines.append(f"{indent}{indent}FROM {sirius_table_name}\n")
        sql_lines.append(f"{indent}{indent}WHERE clientsource = 'CASRECMIGRATION'\n")
        sql_lines.append(f"{indent}{indent}ORDER BY caserecnumber ASC\n")
        # sql_lines.append(f"{indent}{indent}LIMIT 10\n")
        sql_lines.append(f"{indent}) as sirius_data\n")
        sql_lines.append(");\n\n")


def build_results_sql():
    sql_file = open(sql_path / "get_validation_results.sql", 'w')
    reported_mappings = []
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        reported_mappings.append(f"SELECT '{mapping}', (SELECT count(*) FROM {exception_table_name})\n")
    separator = 'UNION\n'
    sql = separator.join(reported_mappings)
    sql_file.writelines(sql)
    sql_file.close()


def show_results(conn_target):
    build_results_sql()
    results_df = df_from_sql_file(
        sql_path, "get_validation_results.sql", conn_target
    )
    print(
        tabulate(
            results_df,
            ['mapping', 'exceptions'],
            tablefmt="psql"
        )
    )


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose):
    set_logging_level(verbose)
    log.info(log_title(message="Validation"))

    # mapping_report()

    copy_schema(
        log=log,
        sql_path=shared_sql_path,
        from_config=config.db_config["migration"],
        from_schema=config.schemas["pre_transform"],
        to_config=config.db_config["target"],
        to_schema=config.schemas["casrec_csv"]
    )

    sql_lines = []

    log.info("Generate Exception Tables SQL")
    build_exception_tables(sql_lines)

    log.info("Generate Validation SQL")
    build_validation_statements(sql_lines)

    validation_sql_file = open(shared_sql_path / "validation.sql", 'w')
    validation_sql_file.writelines(sql_lines)
    validation_sql_file.close()

    log.info(f"RUN VALIDATION")
    conn_target = psycopg2.connect(config.get_db_connection_string("target"))
    execute_sql_file(shared_sql_path, "validation.sql", conn_target, config.schemas["public"])

    log.info(f"RESULTS")
    show_results(conn_target)


if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
