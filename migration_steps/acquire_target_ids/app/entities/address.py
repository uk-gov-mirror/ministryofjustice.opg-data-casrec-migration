from helpers import execute_insert, df_from_sql_file, execute_sql_file


def load_fixtures(self, conn_target):
    execute_sql_file('fixtures_add_addresses.sql', conn_target)


def fetch_target_ids(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    sirius_addresses_df = df_from_sql_file('select_sirius_addresses.sql', conn_target)
    execute_insert(conn_migration, sirius_addresses_df, f"{schema}.sirius_map_addresses")


def merge_target_ids(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    execute_sql_file('merge_target_addresses.sql', conn_migration, schema)
