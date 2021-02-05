import logging
import os

import pandas as pd
from helpers import get_mapping_dict

from merge_helpers import generate_select_query

log = logging.getLogger("root")

environment = os.environ.get("ENVIRONMENT")
import helpers

config = helpers.get_config(env=environment)

row_limit = config.row_limit
table = "person_caseitem"
fk = {"parent_table": "persons", "parent_col": "id", "fk_col": "person_id"}


mapping_file_name = "person_caseitem_mapping"
sirius_details = get_mapping_dict(
    file_name=mapping_file_name,
    stage_name="sirius_details",
    only_complete_fields=False,
)
source_columns = list(sirius_details.keys())

persons_table = {
    "table_name": "persons",
    "columns": ["id", "caserecnumber"],
    "where": {"type": "actor_client"},
}
cases_table = {
    "table_name": "cases",
    "columns": ["id", "caserecnumber"],
}


def merge_source_into_target(db_config, target_db):
    log.log(config.VERBOSE, "This is a join table")

    schema = db_config["target_schema"]
    conn = db_config["db_connection_string"]

    persons_query = generate_select_query(
        schema=schema,
        table=persons_table["table_name"],
        columns=persons_table["columns"],
        where_clause=persons_table["where"],
    )

    persons_df = pd.read_sql_query(persons_query, conn)

    cases_query = generate_select_query(
        schema=schema, table=cases_table["table_name"], columns=cases_table["columns"]
    )

    cases_df = pd.read_sql_query(cases_query, conn)

    person_caseitem_df = cases_df.merge(
        persons_df,
        how="left",
        left_on="caserecnumber",
        right_on="caserecnumber",
        suffixes=["_case", "_person"],
    )

    person_caseitem_df = person_caseitem_df.drop(columns=["caserecnumber"])
    person_caseitem_df = person_caseitem_df.rename(
        columns={"id_case": "caseitem_id", "id_person": "person_id"}
    )
    person_caseitem_df["method"] = "INSERT"

    target_db.insert_data(
        table_name=table, df=person_caseitem_df, sirius_details=sirius_details
    )
