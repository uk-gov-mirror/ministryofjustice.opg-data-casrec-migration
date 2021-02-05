import json

import pandas as pd
from transform_data import transform
from utilities.generate_source_query import generate_select_string_from_mapping
from utilities.helpers import get_mapping_file

definition = {
    "sheet_name": "addresses (Deputy)",
    "source_table_name": "deputy_address",
    "source_table_additional_columns": ["Dep Addr No"],
    "destination_table_name": "addresses",
}


def insert_addresses_deputies(config, target_db):

    with open(get_mapping_file(file_name="addresses_deputy_mapping")) as mapping_json:
        mapping_dict = json.load(mapping_json)

    source_data_query = generate_select_string_from_mapping(
        mapping=mapping_dict,
        source_table_name=definition["source_table_name"],
        additional_columns=definition["source_table_additional_columns"],
        db_schema=config.etl1_schema,
    )

    source_data_df = pd.read_sql_query(
        sql=source_data_query, con=config.connection_string
    )

    addresses_df = transform.perform_transformations(
        mapping_dict,
        definition,
        source_data_df,
        config.connection_string,
        config.etl2_schema,
    )

    deputyship_query = f"""
        select "Dep Addr No", "Deputy No"
        from {config.etl1_schema}.deputyship
    """

    deputyship_df = pd.read_sql_query(deputyship_query, config.connection_string)
    deputyship_df = deputyship_df.drop_duplicates(["Dep Addr No", "Deputy No"])

    persons_query = (
        f'select "id", "c_deputy_no" from etl2.persons '
        f"where \"type\" = 'actor_deputy';"
    )
    persons_df = pd.read_sql_query(persons_query, config.connection_string)

    addresses_with_deputyno_df = addresses_df.merge(
        deputyship_df, how="inner", left_on="c_dep_addr_no", right_on="Dep Addr No"
    )

    address_depno_persons_df = addresses_with_deputyno_df.merge(
        persons_df,
        how="inner",
        left_on="Deputy No",
        right_on="c_deputy_no",
        suffixes=["_address", "_person"],
    )

    address_depno_persons_df = address_depno_persons_df.rename(
        columns={"id_address": "id", "id_person": "person_id"}
    )

    target_db.insert_data(
        table_name=definition["destination_table_name"], df=address_depno_persons_df
    )
