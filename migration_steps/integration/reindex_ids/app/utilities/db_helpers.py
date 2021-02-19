import logging

import psycopg2


log = logging.getLogger("root")


def generate_select_query(schema, table, columns=None, where_clause=None):
    if columns:
        query = f"SELECT {', '.join(columns)} from {schema}.{table}"
    else:
        query = f"SELECT * from {schema}.{table}"

    if where_clause:
        where = ""
        for i, (item, value) in enumerate(where_clause.items()):
            if i == 0:
                where += " WHERE "
            else:
                where += " AND "

            where += f"{item} = '{value}'"

        query += where

    query += ";"

    return query
