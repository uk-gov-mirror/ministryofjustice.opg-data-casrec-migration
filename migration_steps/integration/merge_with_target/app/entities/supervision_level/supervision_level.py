import json
import logging
import os

import config2
import pandas as pd
from helpers import get_mapping_dict

from merge_helpers import generate_select_query, reindex_new_data, update_foreign_keys

log = logging.getLogger("root")

environment = os.environ.get("ENVIRONMENT")
config = config2.get_config(env=environment)

row_limit = config.row_limit
table = "supervision_level_log"
fk = {"parent_table": "cases", "parent_col": "id", "fk_col": "order_id"}


mapping_file_name = "supervision_level_log_mapping"
sirius_details = get_mapping_dict(
    file_name=mapping_file_name,
    stage_name="sirius_details",
    only_complete_fields=False,
)
source_columns = list(sirius_details.keys())


def merge_source_into_target(db_config, target_db):
    log.log(config.VERBOSE, "This is a data table with a foreign key")
    source_data_query = generate_select_query(
        schema=db_config["source_schema"], table=table, columns=source_columns
    )
    log.debug(f"Getting source data using query {source_data_query}")
    source_data_df = pd.read_sql_query(
        con=db_config["db_connection_string"], sql=source_data_query
    )

    source_data_df["method"] = "INSERT"

    log.log(
        config.DATA,
        f"source_data_df\n{source_data_df.head(n=row_limit).to_markdown()}",
    )

    fk_data_query = generate_select_query(
        schema=db_config["target_schema"],
        table=fk["parent_table"],
        columns=[fk["parent_col"], f"transformation_{fk['parent_col']}"],
    )

    fk_data_df = pd.read_sql_query(
        con=db_config["db_connection_string"], sql=fk_data_query
    )

    new_data_df = reindex_new_data(df=source_data_df, table=table, db_config=db_config)

    new_data_with_fk_links = update_foreign_keys(
        df=new_data_df, parent_df=fk_data_df, fk_details=fk
    )

    target_db.insert_data(
        table_name=table, df=new_data_with_fk_links, sirius_details=sirius_details
    )
