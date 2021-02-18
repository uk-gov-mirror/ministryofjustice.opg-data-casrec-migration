import logging
import psycopg2

from decorators import timer

log = logging.getLogger("root")


@timer
def generate_fk_update_statement(db_schema, table_details):

    tables_with_fks = {
        k: v["fks"] for k, v in table_details.items() if len(v["fks"]) > 0
    }
    update_query = ""

    for table, details in tables_with_fks.items():
        for key in details:
            log.debug(f"Generating UPDATE FK for {table} using fk {key['column']}")
            query = f"""
                UPDATE {db_schema}.{table}
                SET {key['column']} = {key['parent_table']}.{key['parent_column']}
                FROM {db_schema}.{key['parent_table']}
                WHERE {table}.transformation_schema_{key['column']} = {key['parent_table']}.transformation_schema_{key['parent_column']}
                AND {table}.method = 'INSERT';
            """
            update_query += query
    # print(update_query)
    return update_query


@timer
def update_fks(db_config, table_details):
    query = generate_fk_update_statement(
        db_schema=db_config["target_schema"], table_details=table_details
    )
    print(query)

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
