import pandas as pd
from utilities.basic_data_table import get_basic_data_table

definition = {
    "source_table_name": "deputy",
    "source_table_additional_columns": ["Email"],
    "destination_table_name": "phonenumbers",
}

mapping_file_name = "deputy_evening_phonenumbers_mapping"


def insert_phonenumbers_deputies_evening(db_config, target_db):

    sirius_details, phonenos_df = get_basic_data_table(
        db_config=db_config,
        mapping_file_name=mapping_file_name,
        table_definition=definition,
    )

    persons_query = (
        f'select "id", "email" from {db_config["target_schema"]}.persons '
        f"where \"type\" = 'actor_deputy';"
    )
    persons_df = pd.read_sql_query(persons_query, db_config["db_connection_string"])

    persons_df = persons_df[["id", "email"]]

    phonenos_joined_df = phonenos_df.merge(
        persons_df, how="left", left_on="c_email", right_on="email"
    )

    phonenos_joined_df["person_id"] = phonenos_joined_df["id_y"]
    phonenos_joined_df = phonenos_joined_df.drop(columns=["id_y", "email"])
    phonenos_joined_df = phonenos_joined_df.rename(columns={"id_x": "id"})

    target_db.insert_data(
        table_name=definition["destination_table_name"],
        df=phonenos_joined_df,
        sirius_details=sirius_details,
    )
