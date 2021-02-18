from merge_helpers import generate_select_query, calculate_new_uid, reindex_new_data
import pandas as pd
import logging
import psycopg2

from decorators import timer

from table_helpers import get_fk_cols_single_table

log = logging.getLogger("root")


@timer
def move_all_tables(db_config, table_list):
    query = generate_create_tables_query(db_config, table_list)

    connection_string = db_config["db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.commit()


def generate_create_tables_query(db_config, table_list):

    create_tables = ""
    for table, details in table_list.items():
        table_name = table

        fks = get_fk_cols_single_table(table=details)
        keys = [x for x in fks + [details["pk"]] if len(x) > 0]
        select_key_cols = [f"{x} as transformation_schema_{x}" for x in keys]

        log.debug(
            f"Generating CREATE TABLE for {table_name} with extra cols: {', '.join([f'transformation_schema_{x}' for x in keys])}"
        )

        query = f"""
            CREATE TABLE {db_config['target_schema']}.{table_name}
            AS
                SELECT *,
                    null as method,
                     {', '.join(select_key_cols)}
                FROM {db_config['source_schema']}.{table_name};
        """

        create_tables += query

    return create_tables
