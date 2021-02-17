from merge_helpers import generate_select_query, calculate_new_uid, reindex_new_data
import pandas as pd
import logging

log = logging.getLogger("root")


def move_a_table(db_config, target_db, table_name):
    source_data_query = generate_select_query(
        schema=db_config["source_schema"], table=table_name
    )
    log.debug(f"Getting source data using query {source_data_query}")
    source_data_df = pd.read_sql_query(
        con=db_config["db_connection_string"], sql=source_data_query
    )

    # source_data_df = calculate_new_uid(
    #     db_config=db_config, df=source_data_df, table=table_name, column_name="uid"
    # )

    log.info(f"This is where we would work out if we need to insert or update data")

    log.info("Reindexing new data")

    source_data_df = reindex_new_data(
        df=source_data_df, table=table_name, db_config=db_config
    )

    log.info("Inserting new data")

    target_db.insert_data(table_name=table_name, df=source_data_df)
