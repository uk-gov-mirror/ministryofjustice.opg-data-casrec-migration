from helpers import *


def load_fixtures(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Clients")
    max_person_uid = result_from_sql_file('get_max_person_uid.sql', conn_target)
    persons_df = df_from_sql_file('fixtures_select_clients.sql', conn_migration, schema)
    persons_df["uid"] = list(range(max_person_uid + 1, max_person_uid + 11, 1))
    execute_mogrify(conn_target, persons_df, 'persons')


def fetch_target_ids(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Clients")
    sirius_persons_df = df_from_sql_file('select_sirius_clients.sql', conn_target)
    execute_mogrify(conn_migration, sirius_persons_df, f"{schema}.sirius_map_clients")


def merge_target_ids(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Clients")
    execute_sql_file('merge_target_clients.sql', conn_migration, schema)
