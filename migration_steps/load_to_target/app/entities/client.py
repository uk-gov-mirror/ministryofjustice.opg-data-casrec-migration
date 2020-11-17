from helpers import *


def target_update(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Clients")
    persons_df = df_from_sql_file('get_skeleton_clients.sql', conn_migration, schema)

    # transpose id column
    persons_df = persons_df.drop(["id", "sirius_id"], axis=1)
    persons_df = persons_df.rename(columns={"target_id": "id"})

    # these columns not implemented upstream yet so drop them for now
    persons_df = persons_df.drop(["statusdate", "updateddate"], axis=1)

    execute_update(conn_target, persons_df, "persons")


def target_add(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Clients")
    persons_df = df_from_sql_file('get_new_clients.sql', conn_migration, schema)

    # don't send id
    persons_df = persons_df.drop(["id", "sirius_id"], axis=1)
    persons_df["clientsource"] = "CASRECMIGRATION"

    # these columns not implemented upstream yet so drop them for now
    persons_df = persons_df.drop(["statusdate", "updateddate"], axis=1)

    # uid not implemented upstream so here's a workaround
    rowcount = len(persons_df.index)
    max_person_uid = result_from_sql_file('get_max_person_uid.sql', conn_target)
    persons_df["uid"] = list(range(max_person_uid + 1, max_person_uid + rowcount + 1, 1))

    execute_insert(conn_target, persons_df, 'persons')


def reindex_target_ids(config, conn_migration, conn_target):
    schema = config.schemas['pre_migrate']
    print("- Re-index target Client IDs")
    sirius_persons_df = df_from_sql_file('select_sirius_clients.sql', conn_target)

    cursor = conn_migration.cursor()
    cursor.execute('TRUNCATE pre_migrate.sirius_map_clients;')
    conn_migration.commit()

    execute_insert(conn_migration, sirius_persons_df, f"{schema}.sirius_map_clients")
