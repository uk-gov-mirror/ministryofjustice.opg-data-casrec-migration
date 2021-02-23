import os
import sys
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../../shared")
import table_helpers
from typing import List, Dict
import logging
import json

import psycopg2

log = logging.getLogger("root")


def get_duplicate_uids(db_config, uid_sequence_list):
    tables = uid_sequence_list[0]["fields"]

    uid_cte_query = ""
    for i, details in enumerate(tables):
        uid_cte_query_table = f"""
            SELECT {details['column']} from {db_config['source_schema']}.{details['table']}
        """
        if i + 1 < len(tables):
            uid_cte_query_table += " UNION ALL "
        uid_cte_query += uid_cte_query_table

    query = f"""
        WITH uids AS (
            {uid_cte_query}
        ),
        counts AS (
        SELECT
            row_number() OVER (PARTITION BY uid) AS count, uid
        FROM uids
        )

        SELECT  uid as dupes FROM counts WHERE count > 1
    """

    success = False
    report = {"pass": [], "fail": []}

    connection_string = db_config["source_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.rowcount

        if rows == 0:
            success = True
            report = {"pass": [x["table"] for x in tables], "fail": []}
        else:
            result = cursor.fetchall()

            success = False
            report = {"pass": [], "fail": [str(x[0]) for x in result]}

    except (Exception, psycopg2.DatabaseError) as error:

        log.error("Error: %s" % error)
    finally:
        conn.rollback()
        cursor.close()
        conn.close()
    return (success, report)
