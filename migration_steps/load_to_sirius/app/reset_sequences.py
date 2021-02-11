from typing import List, Dict
import logging

import psycopg2

log = logging.getLogger("root")


uid_sequence_list = [
    {
        "sequence_name": "global_uid_seq",
        "fields": [
            {"table": "persons", "column": "uid"},
            {"table": "cases", "column": "uid"},
        ],
    }
]


def reset_all_sequences(sequence_list, db_config):
    for seq in sequence_list:
        log.info(f"Resetting sequence {seq['sequence_name']}")
        reset_sequence(sequence_details=seq, db_config=db_config)


def reset_sequence(sequence_details, db_config):

    query = f"""
        SELECT setval('{sequence_details['sequence_name']}', (SELECT MAX ({sequence_details['column']}) FROM {sequence_details['table']}));
    """

    connection_string = db_config["target_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
