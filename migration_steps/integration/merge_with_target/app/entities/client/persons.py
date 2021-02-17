import logging
import os


import pandas as pd
from helpers import get_mapping_dict
from merge_helpers import calculate_new_uid
from merge_helpers import generate_select_query
from merge_helpers import merge_source_data_with_existing_data
from merge_helpers import reindex_existing_data
from merge_helpers import reindex_new_data


log = logging.getLogger("root")

environment = os.environ.get("ENVIRONMENT")
import helpers

config = helpers.get_config(env=environment)

row_limit = config.row_limit
table = "persons"
match_columns = ["caserecnumber", "firstname", "surname"]

mapping_file_name = "client_persons_mapping"
sirius_details = get_mapping_dict(
    file_name=mapping_file_name,
    stage_name="sirius_details",
    only_complete_fields=False,
)
source_columns = list(sirius_details.keys())
source_conditions = {"type": "actor_client"}


def merge_source_into_target(db_config, target_db):
    log.log(config.VERBOSE, "This is a standard data table")

    source_data_query = generate_select_query(
        schema=db_config["source_schema"],
        table=table,
        columns=source_columns,
        where_clause=source_conditions,
    )
    log.debug(f"Getting source data using query {source_data_query}")
    source_data_df = pd.read_sql_query(
        con=db_config["db_connection_string"], sql=source_data_query
    )

    log.log(
        config.DATA,
        f"source_data_df\n{source_data_df.head(n=row_limit).to_markdown()}",
    )

    existing_data_query = generate_select_query(
        schema=db_config["sirius_schema"], table=table, columns=match_columns + ["id"]
    )
    log.debug(f"Getting existing data using query {existing_data_query}")
    existing_data_df = pd.read_sql_query(
        con=db_config["sirius_db_connection_string"], sql=existing_data_query
    )

    log.log(
        config.DATA,
        f"existing_data_df\n" f"{existing_data_df.head(n=row_limit).to_markdown()}",
    )

    merged_data_df = merge_source_data_with_existing_data(
        source_data_df, existing_data_df, match_columns
    )

    log.info("Adding new UID to new data")
    merged_data_df = calculate_new_uid(
        db_config=db_config, df=merged_data_df, table=table, column_name="uid"
    )

    log.log(
        config.DATA,
        f"merged_data_df\n{merged_data_df.head(n=row_limit).to_markdown()}",
    )
    log.info("Reindexing new data")

    new_data_df = reindex_new_data(df=merged_data_df, table=table, db_config=db_config)

    # log.info("Adding new UID to new data")
    # new_data_df = calculate_new_uid(
    #     db_config=db_config, df=new_data_df, table=table, column_name="uid"
    # )

    log.info("Inserting new data")

    target_db.insert_data(
        table_name=table, df=new_data_df, sirius_details=sirius_details
    )
    log.info("Reindexing existing data")
    existing_data = reindex_existing_data(df=merged_data_df, table=table)

    log.info("Inserting existing data")

    target_db.insert_data(
        table_name=table, df=existing_data, sirius_details=sirius_details
    )
