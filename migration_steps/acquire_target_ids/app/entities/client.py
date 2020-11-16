from helpers import *


def load_fixtures(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']

    print("- Clients")
    max_person_uid = result_from_sql_file('get_max_person_uid.sql', conn_target)
    persons_df = df_from_sql_file('fixtures_select_clients.sql', conn_migration, schema)
    persons_df["uid"] = list(range(max_person_uid + 1, max_person_uid + 11, 1))
    execute_mogrify(conn_target, persons_df, 'persons')
