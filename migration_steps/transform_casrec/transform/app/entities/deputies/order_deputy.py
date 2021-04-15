from transform_data.unique_id import add_unique_id
from utilities.basic_data_table import get_basic_data_table
import pandas as pd
from transform_data.apply_datatypes import reapply_datatypes_to_fk_cols

definition = {
    "source_table_name": "deputy",
    "source_table_additional_columns": ["Deputy No", "Stat"],
    "destination_table_name": "order_deputy",
}

mapping_file_name = "order_deputy_mapping"


def insert_order_deputies(db_config, target_db):

    # Get the standard data from casrec 'deputy' table
    sirius_details, person_df = get_basic_data_table(
        db_config=db_config,
        mapping_file_name=mapping_file_name,
        table_definition=definition,
    )

    # Get ids of deputies that have already been transformed
    existing_deputies_query = f"""
        select c_deputy_no, id from {db_config['target_schema']}.persons
        where casrec_mapping_file_name = 'deputy_persons_mapping';
    """
    existing_deputies_df = pd.read_sql_query(
        existing_deputies_query, db_config["db_connection_string"]
    )

    # use the id of the existing deputy
    existing_deputies_merged_df = person_df.merge(
        existing_deputies_df, how="left", left_on="c_deputy_no", right_on="c_deputy_no"
    )
    existing_deputies_merged_df = existing_deputies_merged_df.rename(
        columns={"id_y": "id"}
    )
    deputies_df = existing_deputies_merged_df.drop(columns=["id_x"])

    # deputyship
    deputyship_query = f"""select "Deputy No", "CoP Case" from {db_config["source_schema"]}.deputyship;"""
    deputyship_df = pd.read_sql_query(
        deputyship_query, db_config["db_connection_string"]
    )

    order_query = (
        f"""select "id", "c_cop_case" from {db_config["target_schema"]}.cases;"""
    )
    order_df = pd.read_sql_query(order_query, db_config["db_connection_string"])

    deputyship_persons_joined_df = deputyship_df.merge(
        deputies_df, how="left", left_on="Deputy No", right_on="c_deputy_no"
    )
    deputyship_persons_joined_df["deputy_id"] = deputyship_persons_joined_df["id"]
    deputyship_persons_joined_df["deputy_id"] = deputyship_persons_joined_df[
        "deputy_id"
    ].astype("Int64")
    deputyship_persons_joined_df = deputyship_persons_joined_df.drop(columns=["id"])

    deputyship_persons_order_df = deputyship_persons_joined_df.merge(
        order_df, how="left", left_on="CoP Case", right_on="c_cop_case"
    )

    deputyship_persons_order_df["order_id"] = deputyship_persons_order_df["id"]
    deputyship_persons_order_df = deputyship_persons_order_df.drop(
        columns=["id", "Deputy No", "CoP Case"]
    )

    deputyship_persons_order_df = deputyship_persons_order_df[
        deputyship_persons_order_df["casrec_mapping_file_name"].notna()
    ]

    deputyship_persons_order_df = add_unique_id(
        db_conn_string=db_config["db_connection_string"],
        db_schema=db_config["target_schema"],
        table_definition=definition,
        source_data_df=deputyship_persons_order_df,
    )

    deputyship_persons_order_df = reapply_datatypes_to_fk_cols(
        columns=["order_id", "deputy_id"], df=deputyship_persons_order_df
    )

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=deputyship_persons_order_df,
        sirius_details=sirius_details,
    )
