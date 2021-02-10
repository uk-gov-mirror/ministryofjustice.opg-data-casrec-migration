from typing import List, Dict
import logging

import psycopg2

log = logging.getLogger("root")


def get_max_value(table, column, db_config):
    connection_string = db_config["sirius_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    query = f"SELECT max({column}) from {db_config['sirius_schema']}.{table};"

    try:
        cursor.execute(query)
        max_id = cursor.fetchall()[0][0]
        if max_id:
            log.debug(f"Max Sirius '{column}' in table '{table}': {max_id}")
            return max_id
        else:
            log.debug(
                f"No data for Sirius '{column}' in table '{table}', setting max_id to 0"
            )
            return 0

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 0


def get_sequence_currval(sequence_name, db_config):
    query = f"""SELECT last_value FROM {sequence_name};"""

    connection_string = db_config["sirius_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        curr_id = cursor.fetchall()[0][0]
        if curr_id:
            log.debug(f"Current value of sequence '{sequence_name}' is {curr_id}")
            return curr_id
        else:
            log.debug(f"No data for Sirius '{sequence_name}' something went wrong")
            return 0

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 0


def check_sequences(sequences: List[Dict], db_config: Dict) -> bool:
    """
    check that the next value of the sequence has been reset correctly
    after the migrated data was inserted
    """

    report = {"pass": [], "fail": []}

    for sequence in sequences:

        current_sequence_value = get_sequence_currval(
            sequence_name=sequence["sequence_name"], db_config=db_config
        )
        max_column_value = get_max_value(
            table=sequence["table"], column=sequence["column"], db_config=db_config
        )

        if current_sequence_value == max_column_value:
            report["pass"].append(sequence["sequence_name"])

        else:
            report["fail"].append(sequence["sequence_name"])

    log.info(report)
    if len(report["fail"]) == 0:
        return True
    else:
        return False
