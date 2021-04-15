import json

from sqlalchemy import create_engine
import logging
import pandas as pd

from helpers import format_error_message

log = logging.getLogger("root")


def update_additional_data_json(db_config, table):
    log.debug("update_additional_data_json")
    schema = db_config["target_schema"]

    additional_data_table_query = f"""
        SELECT id, event, c_sirius_table_id, transformation_schema_c_sirius_table_id FROM {schema}.{table};
    """

    additional_data_table_df = pd.read_sql_query(
        sql=additional_data_table_query, con=db_config["db_connection_string"]
    )

    def add_key(row, new_thing):
        for key, value in row["event"].items():
            if key == "payload":
                value["sirius_table_id"] = new_thing
        return row["event"]

    additional_data_table_df["event"] = additional_data_table_df.apply(
        lambda x: add_key(row=x, new_thing=x["c_sirius_table_id"]), axis=1
    )

    return additional_data_table_df


def update_additional_data_json_statement(db_config, table, df):
    log.debug("update_additional_data_json_statement")

    update_statement = ""

    row_df = df[["id", "event"]]
    for i, row in enumerate(row_df.values.tolist()):

        json_field = json.dumps(row[1])
        json_field = json_field.replace("'", "''")

        row_statement = f"""
            UPDATE {db_config['target_schema']}.{table}
            SET event = '{json_field}'
            WHERE id = {row[0]};
        """
        update_statement += row_statement

    return update_statement


def reindex_additional_data(db_config, table, table_details):
    log.info(f"Reindexing additional_data table '{table}'")
    target_db_engine = create_engine(db_config["db_connection_string"])

    additional_data_df = update_additional_data_json(db_config, table)

    update_statement = update_additional_data_json_statement(
        db_config=db_config, table=table, df=additional_data_df
    )

    try:

        with target_db_engine.begin() as conn:
            conn.execute(update_statement)

    except Exception as e:

        log.error(
            f"Errorrrrr {e}",
            extra={
                "file_name": "",
                "error": format_error_message(e=e),
            },
        )
