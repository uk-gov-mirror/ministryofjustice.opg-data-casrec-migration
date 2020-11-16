from helpers import *


# def load_fixtures(self, conn_target):
#     print("- Associated addresses")
#     execute_sql_file('fixtures_add_addresses.sql', conn_target)
#
#
# def fetch_target_ids(config, conn_migration, conn_target):
#     schema = config.schemas['pre_migrate']
#     print("- Associated Addresses")
#     sirius_addresses_df = df_from_sql_file('select_sirius_addresses.sql', conn_target)
#     execute_mogrify(conn_migration, sirius_addresses_df, f"{schema}.sirius_map_addresses")
#
#
# def merge_target_ids(config, conn_migration, conn_target):
#     schema = config.schemas['pre_migrate']
#     print("- Associated addresses")
#     execute_sql_file('merge_target_addresses.sql', conn_migration, schema)


def target_update(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Addresses")
    addresses_df = df_from_sql_file('get_skeleton_addresses.sql', conn_migration, schema)

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
    print("- Addresses")
    addresses_df = df_from_sql_file('get_new_addresses.sql', conn_migration, schema)

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
    print("- Re-merge target Client IDs")
    execute_sql_file('merge_target_addresses.sql', conn_migration, schema)
