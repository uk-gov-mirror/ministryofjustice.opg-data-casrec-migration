from utilities.basic_data_table import get_basic_data_table
import pandas as pd

definition = {
    "source_table_name": "deputy_address",
    "source_table_additional_columns": ["Dep Addr No"],
    "destination_table_name": "addresses",
}

mapping_file_name = "deputy_addresses_mapping"


def insert_addresses_deputies(db_config, target_db):

    sirius_details, addresses_df = get_basic_data_table(
        db_config=db_config,
        mapping_file_name=mapping_file_name,
        table_definition=definition,
    )

    deputyship_query = f"""
        select "Dep Addr No", "Deputy No"
        from {db_config['source_schema']}.deputyship
    """

    deputyship_df = pd.read_sql_query(
        deputyship_query, db_config["db_connection_string"]
    )

    address_deputyship_joined_df = addresses_df.merge(
        deputyship_df, how="left", left_on="c_dep_addr_no", right_on="Dep Addr No"
    )

    deputy_persons_query = f"""
        select c_deputy_no, id as person_id
        from {db_config['target_schema']}.persons
        where casrec_mapping_file_name = 'deputy_persons_mapping'
    """

    deputy_persons_df = pd.read_sql_query(
        deputy_persons_query, db_config["db_connection_string"]
    )

    address_persons_joined_df = address_deputyship_joined_df.merge(
        deputy_persons_df, how="left", left_on="Deputy No", right_on="c_deputy_no"
    )

    address_persons_joined_df = address_persons_joined_df.drop(
        columns=["Dep Addr No", "Deputy No"]
    )

    address_persons_joined_df["person_id"] = (
        address_persons_joined_df["person_id"]
        .fillna(0)
        .astype(int)
        .astype(object)
        .where(address_persons_joined_df["person_id"].notnull())
    )

    address_persons_joined_df = address_persons_joined_df.drop_duplicates()

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=address_persons_joined_df,
        sirius_details=sirius_details,
    )
