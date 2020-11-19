import os
from db_helpers import df_from_sql_file, execute_update, execute_insert, execute_sql_file
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sql_path = current_path / '../sql'


def target_update(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    addresses_df = df_from_sql_file(sql_path, 'get_skeleton_addresses.sql', conn_migration, schema)

    # transpose id column
    addresses_df = addresses_df.drop(["id", "sirius_id", "person_id"], axis=1)
    addresses_df = addresses_df.rename(columns={"target_id": "id"})
    addresses_df = addresses_df.rename(columns={"sirius_person_id": "person_id"})
    addresses_df["isairmailrequired"] = addresses_df["isairmailrequired"].replace(
        {"True": True, "False": False}
    )

    # these columns were added upstream so drop them
    addresses_df = addresses_df.drop(["c_case","caserecnumber"], axis=1)

    execute_update(conn_target, addresses_df, "addresses")


def target_add(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    addresses_df = df_from_sql_file(sql_path, 'get_new_addresses.sql', conn_migration, schema)

    # don't send id
    addresses_df = addresses_df.drop(["id", "sirius_id"], axis=1)

    # transpose person id column
    addresses_df = addresses_df.drop(["person_id"], axis=1)
    addresses_df = addresses_df.rename(columns={"sirius_person_id": "person_id"})
    addresses_df["isairmailrequired"] = addresses_df["isairmailrequired"].replace(
        {"True": True, "False": False}
    )

    # these columns were added upstream so drop them
    addresses_df = addresses_df.drop(["c_case","caserecnumber"], axis=1)

    execute_insert(conn_target, addresses_df, "addresses")


def reindex_target_ids(config, conn_migration):
    schema = config.schemas['pre_migrate']
    execute_sql_file(sql_path, 'merge_target_addresses.sql', conn_migration, schema)
