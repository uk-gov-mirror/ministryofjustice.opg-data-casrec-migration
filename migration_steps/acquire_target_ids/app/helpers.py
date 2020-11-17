import os
import psycopg2
from pathlib import Path
import pandas as pd
import numpy as np

from psycopg2.extensions import register_adapter, AsIs
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sql_path = current_path / 'sql'


def execute_sql_file(filename, conn, schema='public', return_cursor=False):
    cursor = conn.cursor()
    sql_file = open(sql_path / filename, 'r')
    try:
        cursor.execute(sql_file.read().replace('{schema}', str(schema)))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    if return_cursor:
        return cursor
    else:
        cursor.close()


def create_from_template(template_filename, write_filename, search, replace):
    template = open(sql_path / template_filename, "r")
    write_file = open(sql_path / write_filename, "w+")
    for line in template:
        write_file.write(line.replace(search, str(replace)))
    template.close()
    write_file.close()


def execute_generated_sql(template_filename, search, replace, conn):
    sql_filename = template_filename.replace("template.", "")
    create_from_template(template_filename, sql_filename, search, replace)
    execute_sql_file(sql_path / sql_filename, conn)
    os.remove(sql_path / sql_filename)


def result_from_sql_file(filename, conn):
    cursor = execute_sql_file(filename, conn, return_cursor=True)
    result = cursor.fetchone()[0]
    cursor.close()
    return result


def df_from_sql_file(filename, conn, schema="public"):
    sql_file = open(sql_path / filename, 'r')
    sql = sql_file.read().replace('{schema}', str(schema))
    return pd.read_sql_query(sql, con=conn, index_col=None)


# https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
def execute_mogrify(conn, df, table):
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    """

    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]

    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))

    cursor = conn.cursor()
    row_str_template = ','.join(['%s']*len(df.columns))
    values = [cursor.mogrify('('+row_str_template+')', tup).decode('utf8') for tup in tuples]
    query = "INSERT INTO %s(%s) VALUES " % (table, cols) + ",".join(values)

    try:
        cursor.execute(query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()
