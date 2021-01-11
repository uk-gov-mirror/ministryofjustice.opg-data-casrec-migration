from utilities.basic_data_table import get_basic_data_table

definition = {
    "sheet_name": "persons (Client)",
    "source_table_name": "pat",
    "source_table_additional_columns": ["Term Type"],
    "destination_table_name": "persons",
}

mapping_file_name = "client_persons_mapping"


def insert_persons_clients(db_config, target_db):

    sirius_details, persons_df = get_basic_data_table(
        mapping_file_name=mapping_file_name,
        table_definition=definition,
        db_config=db_config,
    )

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=persons_df,
        sirius_details=sirius_details,
    )
