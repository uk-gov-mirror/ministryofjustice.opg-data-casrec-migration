import os
import sys
from pathlib import Path

from pandas._testing import assert_frame_equal

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../../shared")

import pandas as pd

environment = os.environ.get("ENVIRONMENT")
import helpers

config = helpers.get_config(env=environment)


def df_from_sql_file(sql_path, filename, conn, replacements=None, sort_col=None):
    sql_file = open(f"{sql_path}/{filename}", "r")

    sql = sql_file.read()
    query = sql

    if replacements:

        for k, v in replacements.items():
            if isinstance(v, list):
                query = query.replace(str(k), ", ".join([f"'{x}'" for x in v]))
            query = query.replace(str(k), str(v))

    print(query)

    df = pd.read_sql_query(query, con=conn, index_col=None)

    df.replace([None, ""], "", inplace=True)

    if sort_col:
        return df.sort_values(by=[sort_col])
    else:
        return df


def get_test_sample(conn, sample_percentage=10):
    schema = config.schemas["pre_transform"]
    query = f'SELECT "Case" from {schema}.pat'

    df = pd.read_sql_query(query, conn, index_col=None)

    df = df.sample(frac=sample_percentage / 100, replace=False, random_state=1)

    return df["Case"].tolist()


def test_fk_links(sample_percentage=13):
    sql_path = "./sql"
    conn = config.get_db_connection_string("migration")
    test_case_nos = get_test_sample(conn=conn, sample_percentage=sample_percentage)
    sort_col = "caserecnumber"

    print(f"Testing {len(test_case_nos)} cases ({sample_percentage}%)")

    original_data_replacements = {
        "schema": config.schemas["pre_transform"],
        "test_case_list": test_case_nos,
    }

    merged_data_replacements = {
        "schema": config.schemas["integration"],
        "test_case_list": test_case_nos,
    }

    original_data = df_from_sql_file(
        sql_path=sql_path,
        filename="original_data.sql",
        conn=conn,
        replacements=original_data_replacements,
        sort_col=sort_col,
    )

    merged_data = df_from_sql_file(
        sql_path=sql_path,
        filename="migrated_data.sql",
        conn=conn,
        replacements=merged_data_replacements,
        sort_col=sort_col,
    )

    assert_frame_equal(
        original_data.reset_index(drop=True), merged_data.reset_index(drop=True)
    )
