from utilities.basic_data_table import get_basic_data_table

definition = {
    "source_table_name": "deputy",
    "source_table_additional_columns": ["Deputy No", "Special"],
    "destination_table_name": "persons",
}

mapping_file_name = "deputy_persons_mapping"


def insert_persons_deputies(db_config, target_db):

    sirius_details, persons_df = get_basic_data_table(
        db_config=db_config,
        mapping_file_name=mapping_file_name,
        table_definition=definition,
    )

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=persons_df,
        sirius_details=sirius_details,
    )
