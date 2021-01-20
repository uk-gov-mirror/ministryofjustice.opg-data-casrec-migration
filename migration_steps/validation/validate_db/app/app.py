import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from config2 import get_config
from dotenv import load_dotenv
import helpers
from db_helpers import *
import logging
import custom_logger
import click
import pandas as pd

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

conn_target = psycopg2.connect(config.get_db_connection_string("target"))


def set_logging_level(verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")


def get_mapping_report_df():
    file_path = mapping_path / "summary/mapping_progress_summary.json"
    summary_dict = json.load(open(file_path))

    mappings = []
    for worksheet, worksheet_summary in summary_dict['worksheets'].items():
        if worksheet in mappings_to_run:
            mappings.append([worksheet] + list(worksheet_summary.values()))

    return pd.DataFrame.from_records(
        mappings,
        columns=['mapping', 'rows', 'unmapped', 'mapped', 'complete']
    )


def get_validation_exceptions_df(conn_target):
    return df_from_sql_file(
        sql_path, "get_validation_results.sql", conn_target
    )


def get_sirius_table(mapping):
    mapping_name_to_table = {
        "client_persons": "persons",
        "client_addresses": "addresses",
        "client_phonenumbers": "phonenumbers"
    }
    return mapping_name_to_table.get(mapping, mapping)


def get_exception_table(mapping):
    return f"casrec_migration_exceptions_{mapping}"


def build_exception_tables(sql_lines):
    #drop all possible exception tables from last run
    for mapfile in helpers.get_all_mapped_fields().keys():
        sql_lines.append(f"DROP TABLE IF EXISTS {get_exception_table(mapfile)};\n")
    sql_lines.append("\n\n")

    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        map_dict = helpers.get_mapping_dict(
            file_name=mapping + '_mapping',
            only_complete_fields=True,
            include_pk=False
        )
        sql_lines.append(f"CREATE TABLE {exception_table_name}(\n")
        separator = ',\n'
        cols = separator.join([f"{indent}{sirius_col} text default NULL" for sirius_col in map_dict.keys()])
        sql_lines.append(cols)
        sql_lines.append("\n);\n\n")


def build_lookup_functions(sql_lines):
    #drop all the lookup tables from last run
    for lookup_name, lookup in helpers.get_all_lookup_dicts().items():
        sql_lines.append(f"DROP FUNCTION IF EXISTS {lookup_name}(character varying);\n")
    sql_lines.append("\n\n")

    for lookup_name, lookup in helpers.get_all_lookup_dicts().items():
        sql_lines.append(f"CREATE OR REPLACE FUNCTION {lookup_name}(lookup_key varchar default null) RETURNS TEXT AS\n")
        sql_lines.append(f"$$\n")
        sql_lines.append(f"{indent}SELECT CASE\n")
        for k, v in lookup.items():
            sirius_value = v['sirius_mapping'].replace("'", "''")
            sql_lines.append(f"{indent}{indent}WHEN ($1 = '{k}') THEN '{sirius_value}'\n")
        sql_lines.append(f"{indent}END\n")
        sql_lines.append(f"{indent}FROM cases\n")
        sql_lines.append("$$ LANGUAGE sql;\n\n\n")


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


def format_casrec_col_sql(mapping, col):
    if mapping["sirius_details"]["data_type"] in ["date"]:
        col_sql = f"CAST(NULLIF(TRIM({col}), '') AS DATE)"
    elif mapping["sirius_details"]["data_type"] in ["datetime"]:
        if 'current_date' == mapping["transform_casrec"]["calculated"]:
            col_sql = f"CAST(NULLIF(TRIM({col}), '') AS DATE)"
        else:
            col_sql = f"CAST(NULLIF(TRIM({col}), '') AS TIMESTAMP(0))"
    elif mapping["sirius_details"]["data_type"] in ["bool", "int"]:
        col_sql = col
    else:
        col_sql = f'NULLIF(TRIM({col}), \'\')'

    return col_sql


def build_sirius_cols(map_dict):
    sirius_cols = []
    for k, v in map_dict.items():
        if 'current_date' == v["transform_casrec"]["calculated"]:
            col_string = f"CAST({k} AS DATE) AS {k}"
        else:
            col_string = f"{k} AS {k}"

        sirius_cols.append(f"{indent}{indent}{indent}{col_string}")

    separator = ',\n'
    return separator.join(sirius_cols)


def build_casrec_cols(map_dict):
    casrec_cols = []
    casrec_tables = []
    for k, v in map_dict.items():
        if v["transform_casrec"]["casrec_table"]:
            casrec_col_table = v["transform_casrec"]["casrec_table"].lower()
            casrec_col_name = v["transform_casrec"]["casrec_column_name"]
            casrec_tables.append(config.schemas['casrec_csv'] + '.' + casrec_col_table)
            col = f'{casrec_col_table}."{casrec_col_name}"'
            if '' != v["transform_casrec"]["lookup_table"]:
                db_lookup_func = v["transform_casrec"]["lookup_table"]
                col = f'{db_lookup_func}({col})'
        elif '' != v["transform_casrec"]["default_value"]:
            col = format_default_value(v)
        elif '' != v["transform_casrec"]["calculated"]:
            col = format_calculated_value(v)
        casrec_cols.append(
            f"{indent}{indent}{indent}{format_casrec_col_sql(v, col)} AS {k}"
        )

    separator = ',\n'
    casrec_cols = separator.join(casrec_cols)
    separator = ','
    casrec_tables = separator.join(set(casrec_tables))
    return casrec_cols, casrec_tables


def build_validation_statements(sql_lines):
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        sirius_table_name = get_sirius_table(mapping)
        map_dict = helpers.get_mapping_dict(
            file_name=mapping + '_mapping',
            only_complete_fields=True,
            include_pk=False
        )

        casrec_cols, casrec_tables = build_casrec_cols(map_dict)
        sirius_cols = build_sirius_cols(map_dict)

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


def write_validation_sql(sql_lines):
    validation_sql_path = shared_sql_path / "validation.sql"
    validation_sql_file = open(validation_sql_path, 'w')
    validation_sql_file.writelines(sql_lines)
    validation_sql_file.close()
    log.info(f"Saved to file: {validation_sql_path}\n")


def write_get_exceptions_sql():
    sql_file = open(sql_path / "get_validation_results.sql", 'w')
    reported_mappings = []
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        reported_mappings.append(f"SELECT '{mapping}' AS mapping, (SELECT count(*) FROM {exception_table_name})\n")
    separator = 'UNION\n'
    sql = separator.join(reported_mappings)
    sql_file.writelines(sql)
    sql_file.close()


def pre_validation():
    log.info(f"COPY CASREC CSV DATA TO TARGET DB FOR COMPARISON WORK")
    copy_schema(
        log=log,
        sql_path=shared_sql_path,
        from_config=config.db_config["migration"],
        from_schema=config.schemas["pre_transform"],
        to_config=config.db_config["target"],
        to_schema=config.schemas["casrec_csv"]
    )

    log.info(f"GENERATE SQL")
    sql_lines = []

    log.info("- Exception Tables")
    build_exception_tables(sql_lines)

    log.info("- Lookup Functions")
    build_lookup_functions(sql_lines)

    log.info("- Validation SQL")
    build_validation_statements(sql_lines)
    write_validation_sql(sql_lines)


def post_validation():
    log.info("REPORT")
    mapping_df = get_mapping_report_df()
    write_get_exceptions_sql()
    exceptions_df = get_validation_exceptions_df(conn_target)
    report_df = mapping_df.merge(exceptions_df, on='mapping')
    headers = ["Casrec Mapping", "Rows", "Unmapped", "Mapped", "Complete (%)", "Exceptions"]
    print(tabulate(report_df, headers, tablefmt="psql"))


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose):
    set_logging_level(verbose)
    log.info(helpers.log_title(message="Validation"))

    pre_validation()

    log.info("RUN VALIDATION")
    execute_sql_file(shared_sql_path, "validation.sql", conn_target, config.schemas["public"])
    log.info("- ok\n")

    post_validation()



if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
