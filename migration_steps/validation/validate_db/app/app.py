import sys
import os
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../shared")

import time
import psycopg2
from helpers import get_config
from dotenv import load_dotenv
import helpers
from db_helpers import *
from helpers import *
import logging
import custom_logger
import click
import pandas as pd

from tabulate import tabulate
import json
from datetime import datetime
import pprint
import boto3

pp = pprint.PrettyPrinter(indent=4)

env_path = current_path / "../../../../.env"
shared_path = current_path / "../../../shared"
shared_sql_path = shared_path / "sql"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)

# logging
log = logging.getLogger("root")
log.addHandler(custom_logger.MyHandler())
config.custom_log_level()
verbosity_levels = config.verbosity_levels

is_staging = False
conn_target = None
target_schema = None
source_schema = config.schemas["pre_transform"]

mappings_to_run = [
    # "client_persons",
    "client_addresses",
    # "client_phonenumbers",
    # "cases",
    # "person_caseitem"
]

results_sqlfile = "get_validation_results.sql"
validation_sqlfile = "validation.sql"
total_exceptions_sqlfile = "get_exceptions_total.sql"
host = os.environ.get("DB_HOST")
ci = os.getenv("CI")
bucket_name = f"casrec-migration-{environment.lower()}"
account = os.environ["SIRIUS_ACCOUNT"]
session = boto3.session.Session()
sql_lines = []


def set_logging_level(verbose):
    try:
        log.setLevel(verbosity_levels[verbose])
    except KeyError:
        log.setLevel("INFO")
        log.info(f"{verbose} is not a valid verbosity level")


def get_mapping_report_df():
    file_path = shared_path / "mapping_definitions/summary/mapping_progress_summary.json"
    summary_dict = json.load(open(file_path))

    mappings = []
    for worksheet, worksheet_summary in summary_dict["worksheets"].items():
        if worksheet in mappings_to_run:
            mappings.append([worksheet] + list(worksheet_summary.values()))

    return pd.DataFrame.from_records(
        mappings, columns=["mapping", "rows", "unmapped", "mapped", "complete"]
    )


def get_exception_table(mapping):
    return f"exceptions_{mapping}"


def build_exception_tables():
    # drop all possible exception tables from last run
    for mapfile in helpers.get_all_mapped_fields().keys():
        sql_add(
            f"DROP TABLE IF EXISTS {source_schema}.{get_exception_table(mapfile)};"
        )
    sql_add("\n")

    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        map_dict = helpers.get_mapping_dict(
            file_name=mapping + "_mapping", only_complete_fields=True, include_pk=False
        )
        exclude_cols = validation_dict[mapping]['exclude']

        sql_add(f"CREATE TABLE {source_schema}.{exception_table_name}(")
        sql_add("caserecnumber text default NULL,", 1)

        # overridden cols (normally run through plsql transform routines)
        for col in validation_dict[mapping]['overriden']:
            sql_add(f"{col} text default NULL,", 1)

        # other columns
        separator = ",\n"
        sql_add(separator.join(
            [
                f"    {col} text default NULL"
                for col in map_dict.keys() if col not in exclude_cols
            ]
        ))
        sql_add("\n);", 0, 2)


def build_lookup_functions():
    # drop all the lookup tables from last run
    for lookup_name, lookup in helpers.get_all_lookup_dicts().items():
        sql_add(f"DROP FUNCTION IF EXISTS {source_schema}.{lookup_name}(character varying);")
    sql_add("\n\n")

    for lookup_name, lookup in helpers.get_all_lookup_dicts().items():
        sql_add(
            f"CREATE OR REPLACE FUNCTION {source_schema}.{lookup_name}(lookup_key varchar default null) RETURNS TEXT AS\n"
        )
        sql_add(f"$$\n")
        sql_add(f"SELECT CASE", 1)
        for k, v in lookup.items():
            try:
                sirius_value = v["sirius_mapping"].replace("'", "''")
            except AttributeError:
                sirius_value = v["sirius_mapping"]
            sql_add(f"WHEN ($1 = '{k}') THEN '{sirius_value}'", 2)
        sql_add("END", 1)
        sql_add("$$ LANGUAGE sql;", 0, 3)


def format_calculated_value(mapping):
    callables = {
        "current_date": "'"
        + datetime.now().strftime("%Y-%m-%d")
        + "'"  # just do today's date
    }
    return callables.get(mapping["transform_casrec"]["calculated"])


def format_default_value(mapping):
    default_value = mapping["transform_casrec"]["default_value"]
    if mapping["sirius_details"]["data_type"] in ["date", "datetime", "str"]:
        default_value = f"'{default_value}'"
    return default_value


def wrap_sirius_datatype_functions(mapping, col_name):
    sql = col_name
    if "current_date" == mapping["transform_casrec"]["calculated"]:
        sql = f"CAST({col_name} AS DATE)"
    return sql


def get_sirius_col_name(mapping, col_name):
    col_table = mapping["sirius_details"]["table_name"]
    return f"{col_table}.{col_name}"


def build_sirius_cols(map_dict, exclude):
    sirius_cols = []
    filtered = {k: v for (k, v) in map_dict.items() if k not in exclude}
    for k, v in filtered.items():
        sirius_cols.append(
            f"                {wrap_sirius_datatype_functions(v, get_sirius_col_name(v, k))} AS {k}"
        )

    separator = ",\n"
    return separator.join(sirius_cols)


def wrap_transformation_func(map_dict, col):
    if "" != map_dict["transform_casrec"]["requires_transformation"]:
        transform_func = map_dict["transform_casrec"]["requires_transformation"]
        col = f"transf_{transform_func}({col})"
    return col


def wrap_casrec_col_conversion_functions(mapping):
    col = wrap_transformation_func( mapping, get_casrec_col_source(mapping))
    datatype = mapping["sirius_details"]["data_type"]
    if datatype in ["date"]:
        wrapped_col = f"CAST(NULLIF(NULLIF(TRIM({col}), 'NaT'), '') AS DATE)"
    elif datatype in ["datetime"]:
        if "current_date" == mapping["transform_casrec"]["calculated"]:
            wrapped_col = f"CAST(NULLIF(TRIM({col}), '') AS DATE)"
        else:
            wrapped_col = (
                f"CAST(NULLIF(NULLIF(TRIM({col}), 'NaT'), '') AS TIMESTAMP(0))"
            )
    elif datatype in ["bool", "int"]:
        wrapped_col = col
    else:
        wrapped_col = f"NULLIF(TRIM({col}), '')"

    return wrapped_col


def get_casrec_col_source(mapping):
    col = ''
    print(mapping)
    if mapping["transform_casrec"]["casrec_table"]:
        col = get_full_casrec_column_name(mapping)
        if "" != mapping["transform_casrec"]["lookup_table"]:
            db_lookup_func = mapping["transform_casrec"]["lookup_table"]
            col = f"{source_schema}.{db_lookup_func}({col})"
    elif "" != mapping["transform_casrec"]["default_value"]:
        col = format_default_value(mapping)
    elif "" != mapping["transform_casrec"]["calculated"]:
        col = format_calculated_value(mapping)

    return col


def build_casrec_cols(map_dict, exclude):
    casrec_cols = []

    filtered = {k:v for (k,v) in map_dict.items() if k not in exclude}
    for k, v in filtered.items():
        if get_casrec_col_source(v) != '':
            casrec_cols.append(
                f"                {wrap_casrec_col_conversion_functions(v)} AS {k}"
            )

    separator = ",\n"
    casrec_cols = separator.join(casrec_cols)
    return casrec_cols


def get_full_casrec_column_name(mapping):
    casrec_col_table = mapping["transform_casrec"]["casrec_table"].lower()
    casrec_col_name = mapping["transform_casrec"]["casrec_column_name"]
    return f'{casrec_col_table}."{casrec_col_name}"'


def get_validation_dict():
    file_path = shared_path / "validation_mapping.json"
    validation_dict = json.load(open(file_path))
    return validation_dict


def build_validation_statements():
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        map_dict = helpers.get_mapping_dict(
            file_name=mapping + "_mapping", only_complete_fields=True, include_pk=False
        )
        exclude_cols = validation_dict[mapping]['exclude']
        casrec_cols = build_casrec_cols(map_dict, exclude_cols)
        casrec_overridden_cols = validation_dict[mapping]['casrec']['overriden']
        sirius_cols = build_sirius_cols(map_dict, exclude_cols)
        sirius_overridden_cols = validation_dict[mapping]['sirius']['overriden']

        sql_add(f"-- {mapping}")
        sql_add(f"INSERT INTO {source_schema}.{exception_table_name}(")

        # CASREC half
        sql_add("SELECT * FROM(", 1)
        sql_add("SELECT DISTINCT", 2)
        sql_add("pat.\"Case\" AS caserecnumber,", 3)

        # overridden cols (normally run through plsql transform routines)
        for colname, col in casrec_overridden_cols.items():
            sql_add(f"{col} AS {colname},", 3)

        # standard cols
        sql_add(f"{casrec_cols}")

        # FROM, with JOINs
        sql_add(f"FROM {source_schema}.{validation_dict[mapping]['casrec']['from_table']}", 2)

        #ORDER
        sql_add("ORDER BY caserecnumber ASC", 2)
        sql_add(") as csv_data", 1)
        sql_add("EXCEPT", 1)

        # SIRIUS half
        sql_add("SELECT * FROM(", 1)
        sql_add("SELECT DISTINCT", 1)

        #casrec col
        sql_add("persons.caserecnumber AS caserecnumber,", 3)

        # overridden cols (normally run through plsql transform routines)
        for colname, col in sirius_overridden_cols.items():
            sql_add(f"{col} AS {colname},", 3)

        # standard cols
        sql_add(sirius_cols)

        # FROM, with JOINs
        sql_add(f"FROM {target_schema}.{validation_dict[mapping]['sirius']['from_table']}", 3)
        for join in validation_dict[mapping]['sirius']['joins']:
            sql_add(f"{join}", 2)

        # WHERE
        sql_add("WHERE clientsource = 'CASRECMIGRATION'", 2)

        # ORDER
        sql_add("ORDER BY caserecnumber ASC", 2)
        sql_add(") as sirius_data", 1)
        sql_add(");", 0, 2)


def sql_add(sql, indent_level=0, line_breaks=1):
    global sql_lines
    indent = "    " * indent_level
    breaks = "\n" * line_breaks
    sql_lines.append(f"{indent}{sql}{breaks}")


def build_column_validation_statements():
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        map_dict = helpers.get_mapping_dict(
            file_name=mapping + "_mapping", only_complete_fields=True, include_pk=False
        )
        exclude_cols = validation_dict[mapping]['exclude']
        casrec_cols = build_casrec_cols(map_dict, exclude_cols)
        casrec_overridden_cols = validation_dict[mapping]['casrec']['overriden']
        sirius_cols = build_sirius_cols(map_dict, exclude_cols)
        sirius_overridden_cols = validation_dict[mapping]['sirius']['overriden']

        exception_table = f"{source_schema}.{get_exception_table(mapping)}"

        sql_add(f"ALTER TABLE {exception_table} DROP COLUMN IF EXISTS vary_columns;")
        sql_add(f"ALTER TABLE {exception_table} ADD vary_columns varchar(255)[];", 0, 2)

        # if "caserecnumber" in map_dict:
        #     del map_dict["caserecnumber"]

        # # overridden cols (normally run through plsql transform routines)
        # for colname, col in sirius_overridden_cols.items():
        #     sql_add(f"                {col} AS {colname},", 3)

        filtered = {k: v for (k, v) in map_dict.items() if k not in exclude_cols}
        for k, v in filtered.items():
            sql_add(f"-- {k}")
            sql_add(f"UPDATE {exception_table}")
            sql_add(f"SET vary_columns = array_append(vary_columns, '{k}')")
            sql_add("WHERE caserecnumber IN (")

            # OUTER SELECT
            sql_add(f"SELECT caserecnumber FROM (", 1)
            # casrec half
            sql_add("SELECT * FROM(", 2)
            sql_add("SELECT", 3)
            sql_add("exc_table.caserecnumber,", 4)
            # tested column
            sql_add(f"{wrap_casrec_col_conversion_functions(v)} AS {k}", 4)
            sql_add(f"FROM {source_schema}.pat", 3)
            sql_add(f"LEFT JOIN {exception_table} exc_table", 3)
            sql_add('ON exc_table.caserecnumber = pat."Case"', 4)
            sql_add("WHERE exc_table.caserecnumber IS NOT NULL", 3)
            sql_add("ORDER BY exc_table.caserecnumber", 3)
            sql_add(") as csv_data", 2)
            sql_add("EXCEPT", 2)

            # sirius half
            sql_add("SELECT * FROM(", 2)
            sql_add("SELECT", 3)
            sql_add("exc_table.caserecnumber,", 4)
            # tested column
            sql_add(f"{get_sirius_col_name(v, k)} AS {k}", 4)
            sql_add(f"FROM {target_schema}.{validation_dict[mapping]['sirius']['from_table']}", 3)
            for join in validation_dict[mapping]['sirius']['joins']:
                sql_add(f"{join}", 3)
            sql_add(f"LEFT JOIN {exception_table} exc_table", 3)
            sql_add("ON exc_table.caserecnumber = persons.caserecnumber", 4)
            sql_add("WHERE exc_table.caserecnumber IS NOT NULL", 3)
            sql_add("ORDER BY exc_table.caserecnumber", 3)
            sql_add(") as sirius_data", 2)
            sql_add(") as vary", 1)
            sql_add(");", 0, 2)


def write_validation_sql():
    global sql_lines
    log.debug(f"Writing to file")
    validation_sql_path = shared_sql_path / validation_sqlfile
    validation_sql_file = open(validation_sql_path, "w")
    validation_sql_file.writelines(sql_lines)
    validation_sql_file.close()
    log.debug(f"Saved to file: {validation_sql_path}")


def write_results_sql():
    sql_file = open(shared_sql_path / results_sqlfile, "w")
    results_rows = []
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        casrec_table_name = validation_dict[mapping]['casrec']['from_table']
        results_rows.append(
            f"SELECT '{mapping}' AS mapping,"
            f"(SELECT COUNT(*) FROM {source_schema}.{casrec_table_name}) as attempted,"
            f"(SELECT COUNT(*) FROM {source_schema}.{exception_table_name}),"
            f"(SELECT CONCAT( CAST( CAST( "
            f"(SELECT COUNT(*) FROM {source_schema}.{exception_table_name}) / "
            f"(SELECT COUNT(*) FROM {source_schema}.{casrec_table_name})::FLOAT AS numeric ) AS TEXT), '%')),"
            f"(SELECT json_agg(vary) AS affected_columns FROM ("
            f"SELECT DISTINCT unnest(vary_columns) as vary FROM {source_schema}.{exception_table_name}"
            f") t1)\n"
        )
    separator = "UNION\n"
    sql_file.writelines(separator.join(results_rows))
    sql_file.close()


def write_get_exception_count_sql():
    sql_file = open(shared_sql_path / total_exceptions_sqlfile, "w")
    sql = f"SELECT SUM(exceptions) FROM (\n"

    ex_tables_sql = []
    for mapping in mappings_to_run:
        exception_table_name = get_exception_table(mapping)
        ex_tables_sql.append(
            f"    SELECT COUNT(*) as exceptions, 'client_persons' "
            f"FROM {source_schema}.{exception_table_name}\n"
        )

    separator = "    UNION\n"
    sql += separator.join(ex_tables_sql)
    sql += ") all_exceptions;"
    sql_file.writelines(sql)
    sql_file.close()


def pre_validation():
    # if is_staging is False:
    #     log.info(f"Validating with SIRIUS")
    #     log.info(f"Copying casrec csv source data to Sirius for comparison work")
    #     copy_schema(
    #         log=log,
    #         sql_path=shared_sql_path,
    #         from_config=config.db_config["migration"],
    #         from_schema=config.schemas["pre_transform"],
    #         to_config=config.db_config["target"],
    #         to_schema=config.schemas["pre_transform"],
    #     )
    # else:
    #     log.info(f"Validating with STAGING schema")

    log.info(f"GENERATE SQL")

    # log.info("- Exception Tables")
    # build_exception_tables()
    #
    # log.info("- Lookup Functions")
    # build_lookup_functions()
    #
    # log.info("- Validation SQL")
    # build_validation_statements()

    log.info("- Column insight")
    build_column_validation_statements()

    log.info(f"Printing Lines:")
    write_validation_sql()


def post_validation():
    log.info("REPORT")
    mapping_df = get_mapping_report_df()
    write_results_sql()
    exceptions_df = df_from_sql_file(shared_sql_path, results_sqlfile, conn_target)
    report_df = mapping_df.merge(exceptions_df, on="mapping")
    headers = [
        "Casrec Mapping",
        "Rows",
        "Unmapped",
        "Mapped",
        "Complete (%)",
        "Attempted",
        "Failed",
        "Fail rate",
        "Mismatches in...",
    ]
    print(tabulate(report_df, headers, tablefmt="psql"))


def set_validation_target():
    global conn_target, target_schema
    db_config = "migration" if is_staging else "target"
    conn_target = psycopg2.connect(config.get_db_connection_string(db_config))
    target_schema = "staging" if is_staging else "public"


def get_exception_count():
    write_get_exception_count_sql()
    return result_from_sql_file(shared_sql_path, total_exceptions_sqlfile, conn_target)


@click.command()
@click.option("-v", "--verbose", count=True)
@click.option("--staging", is_flag=True, default=False)
def main(verbose, staging):
    set_logging_level(verbose)
    log.info(helpers.log_title(message="Validation"))

    global is_staging
    is_staging = staging
    set_validation_target()

    pre_validation()
    #
    # log.info("RUN VALIDATION")
    #
    # execute_sql_file(
    #     shared_sql_path, validation_sqlfile, conn_target, config.schemas["public"]
    # )
    # log.info("- ok\n")

    # post_validation()

    # if get_exception_count() > 0:
    #     exit(1)
    #
    # log.info("No exceptions found: continue...\n")
    # log.info("Adding sql files to bucket...\n")
    #
    # s3 = get_s3_session(session, environment, host)
    # if ci != "true":
    #     for file in os.listdir(shared_sql_path):
    #         file_path = f"{shared_sql_path}/{file}"
    #         s3_file_path = f"validation/sql/{file}"
    #         if file.endswith(".sql"):
    #             upload_file(bucket_name, file_path, s3, log, s3_file_path)


if __name__ == "__main__":
    t = time.process_time()

    log.setLevel(1)
    log.debug(f"Working in environment: {os.environ.get('ENVIRONMENT')}")

    validation_dict = get_validation_dict()

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
