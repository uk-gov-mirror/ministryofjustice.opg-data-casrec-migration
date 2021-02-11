from typing import List, Dict
import logging

import psycopg2

log = logging.getLogger("root")


def get_max_value(fields: Dict, db_config: Dict) -> int:
    connection_string = db_config["sirius_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    actual_max_uid = 0

    for field in fields:
        query = f"SELECT max({field['column']}) from {db_config['sirius_schema']}.{field['table']};"

        try:
            cursor.execute(query)
            max_uid = cursor.fetchall()[0][0]
            if max_uid:
                log.debug(
                    f"Max Sirius '{field['column']}' in table '{field['table']}': {max_uid}"
                )

                if max_uid > actual_max_uid:
                    actual_max_uid = max_uid

            else:
                log.debug(
                    f"No data for Sirius '{field['column']}' in table '{field['table']}', setting max_id to 0"
                )

            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            log.error("Error: %s" % error)
            conn.rollback()
            cursor.close()

        return actual_max_uid


def decode_uid(uid: int) -> int:
    min_uid = 70000000000
    return int(str(uid)[:-1]) - min_uid


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
            cursor.close()
            return curr_id
        else:
            log.debug(f"No data for Sirius '{sequence_name}' something went wrong")
            cursor.close()
            return 0

    except (Exception, psycopg2.DatabaseError) as error:
        log.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 0


def check_uid_sequences(sequences: List[Dict], db_config: Dict) -> bool:
    """
    check that the next value of the sequence has been reset correctly
    after the migrated data was inserted
    """

    report = {"pass": [], "fail": []}

    for sequence in sequences:

        current_sequence_value = get_sequence_currval(
            sequence_name=sequence["sequence_name"], db_config=db_config
        )
        max_column_value = get_max_value(fields=sequence["fields"], db_config=db_config)
        max_seq_value = decode_uid(uid=max_column_value)

        if current_sequence_value == max_seq_value:
            log.debug(
                f"Current sequence value ({current_sequence_value}) == max used value ({max_seq_value})"
            )
            report["pass"].append(sequence["sequence_name"])

        else:
            log.debug(
                f"Current sequence value ({current_sequence_value}) != max used value ({max_seq_value})"
            )
            report["fail"].append(sequence["sequence_name"])

    if len(report["fail"]) == 0:
        return (True, report)
    else:
        return (False, report)
