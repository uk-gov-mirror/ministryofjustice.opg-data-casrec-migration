import logging
import psycopg2

from decorators import timer

log = logging.getLogger("root")


@timer
def match_existing_data(db_config, table_details):
    """
    This is a placeholder for now. Just setting everything as new data for now
    The real matchy script will look WAY more complicated than this!
    """
    default_value = "INSERT"
    log.info(f"(currently just setting every record to '{default_value}')")
    connection_string = db_config["db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    for table in table_details:
        log.debug(f"Setting method on {table} to default_value: '{default_value}'")
        query = f"""
            UPDATE {db_config['target_schema']}.{table}
            SET method = '{default_value}';
        """

        try:
            cursor.execute(query)
        except Exception as e:
            print(e)

    cursor.close()
    conn.commit()
