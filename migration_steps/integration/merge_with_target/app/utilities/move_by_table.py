from merge_helpers import generate_select_query, calculate_new_uid, reindex_new_data
import pandas as pd
import logging

log = logging.getLogger("root")


def move_all_tables(db_config, target_db, table_list):

    for table, details in table_list.items():
        table_name = table

        keys = [x for x in details["fks"] + [details["pk"]] if len(x) > 0]

        source_data_query = generate_select_query(
            schema=db_config["source_schema"], table=table_name
        )
        log.debug(f"Getting source data using query {source_data_query}")
        source_data_df = pd.read_sql_query(
            con=db_config["db_connection_string"], sql=source_data_query
        )

        for key in keys:
            new_key = f"transform_schema_{key}"
            source_data_df[new_key] = source_data_df[key]

        log.info("Inserting new data")

        target_db.insert_data(table_name=table_name, df=source_data_df)
