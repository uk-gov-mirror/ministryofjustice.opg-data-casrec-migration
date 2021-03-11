from utilities.basic_data_table import get_basic_data_table
import pandas as pd
from transform_data import unique_id as process_unique_id
import logging

log = logging.getLogger("root")
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

    log.debug(f"len(addresses_df): {len(addresses_df)}")

    deputyship_query = f"""
        select "Dep Addr No", "Deputy No"
        from {db_config['source_schema']}.deputyship
    """

    deputyship_df = pd.read_sql_query(
        deputyship_query, db_config["db_connection_string"]
    )

    log.debug(f"len(deputyship_df) 1: {len(deputyship_df)}")

    log.debug("deputyship remove na")
    deputyship_df = deputyship_df[deputyship_df["Dep Addr No"].notna()]
    log.debug("deputyship remove empty string")
    deputyship_df = deputyship_df[deputyship_df["Dep Addr No"] != ""]
    log.debug("deputyship convert to float")
    deputyship_df["Dep Addr No"] = deputyship_df["Dep Addr No"].astype("float")
    log.debug("deputyship convert to int32")
    deputyship_df["Dep Addr No"] = deputyship_df["Dep Addr No"].astype("Int32")

    log.debug("addresses_df remove na")
    addresses_df = addresses_df[addresses_df["c_dep_addr_no"].notna()]
    log.debug("addresses_df cnvert to float")
    addresses_df["c_dep_addr_no"] = addresses_df["c_dep_addr_no"].astype("float")
    log.debug("addresses_df convert to int32")
    addresses_df["c_dep_addr_no"] = addresses_df["c_dep_addr_no"].astype("Int32")

    # there are multiple entries for different CoP_Case
    # but the address details are the same
    log.debug("deputyship_df drop duplicates")
    deputyship_df = deputyship_df.drop_duplicates()

    log.debug(f"len(addresses_df) 2: {len(addresses_df)}")

    log.debug("deputyship_df  & address_df merge")
    address_deputyship_joined_df = addresses_df.merge(
        deputyship_df, how="left", left_on="c_dep_addr_no", right_on="Dep Addr No"
    )

    log.debug(f"len(address_deputyship_joined_df): {len(address_deputyship_joined_df)}")

    deputy_persons_query = f"""
        select c_deputy_no, id as person_id
        from {db_config['target_schema']}.persons
        where casrec_mapping_file_name = 'deputy_persons_mapping'
    """

    deputy_persons_df = pd.read_sql_query(
        deputy_persons_query, db_config["db_connection_string"]
    )

    log.debug(f"len(deputy_persons_df): {len(deputy_persons_df)}")

    log.debug("address_deputyship_joined_df  & deputy_persons_df merge")
    address_persons_joined_df = address_deputyship_joined_df.merge(
        deputy_persons_df, how="left", left_on="Deputy No", right_on="c_deputy_no"
    )

    log.debug(f"len(address_persons_joined_df) 1: {len(address_persons_joined_df)}")

    address_persons_joined_df = address_persons_joined_df.drop(
        columns=["Dep Addr No", "Deputy No"]
    )

    log.debug(f"len(address_persons_joined_df) 2: {len(address_persons_joined_df)}")

    address_persons_joined_df["person_id"] = (
        address_persons_joined_df["person_id"]
        .fillna(0)
        .astype(int)
        .astype(object)
        .where(address_persons_joined_df["person_id"].notnull())
    )

    log.debug(f"len(address_persons_joined_df) 3: {len(address_persons_joined_df)}")

    address_persons_joined_df = address_persons_joined_df.drop_duplicates()

    log.debug(f"len(address_persons_joined_df) 4: {len(address_persons_joined_df)}")

    address_persons_joined_df = address_persons_joined_df.drop(columns=["id"])

    log.debug(f"len(address_persons_joined_df) 5: {len(address_persons_joined_df)}")

    address_persons_joined_df = process_unique_id.add_unique_id(
        db_conn_string=db_config["db_connection_string"],
        db_schema=db_config["target_schema"],
        table_definition=definition,
        source_data_df=address_persons_joined_df,
    )

    log.debug(f"len(address_persons_joined_df) 6: {len(address_persons_joined_df)}")

    # some addresses don't seem to match up with people...
    address_persons_joined_df = address_persons_joined_df[
        address_persons_joined_df["person_id"].notna()
    ]

    log.debug(f"len(address_persons_joined_df) 7: {len(address_persons_joined_df)}")

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=address_persons_joined_df,
        sirius_details=sirius_details,
    )
