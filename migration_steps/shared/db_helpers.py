import os
import psycopg2
import pandas as pd
import numpy as np

from psycopg2.extensions import register_adapter, AsIs
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)


def execute_sql_file(sql_path, filename, conn, schema='public'):
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
    cursor.close()


def create_from_template(sql_path, template_filename, write_filename, search, replace):
    template = open(sql_path / template_filename, "r")
    write_file = open(sql_path / write_filename, "w+")
    for line in template:
        write_file.write(line.replace(search, str(replace)))
    template.close()
    write_file.close()


def execute_generated_sql(sql_path, template_filename, search, replace, conn):
    sql_filename = template_filename.replace("template.", "")
    create_from_template(sql_path, template_filename, sql_filename, search, replace)
    execute_sql_file(sql_path, sql_filename, conn)
    os.remove(sql_path / sql_filename)
    conn.commit()


def result_from_sql_file(sql_path, filename, conn):
    cursor = conn.cursor()
    sql_file = open(sql_path / filename, 'r')
    cursor.execute(sql_file.read())
    result = cursor.fetchone()[0]
    cursor.close()
    return result


def df_from_sql_file(sql_path, filename, conn, schema="public"):
    sql_file = open(sql_path / filename, 'r')
    sql = sql_file.read().replace('{schema}', str(schema))
    return pd.read_sql_query(sql, con=conn, index_col=None)


def execute_insert(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]
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


def execute_update(conn, df, table):
    # Just ensure that the primary key is the first column of the dataframe

    cols = list(df.columns)
    pk_col = cols.pop(0)
    colstring = '=%s,'.join(cols)
    colstring += '=%s'
    update_template = f'UPDATE {table} SET {colstring} WHERE {pk_col}='

    cursor = conn.cursor()

    for vals in df.to_numpy():
        query = cursor.mogrify(update_template+str(vals[0]), vals[1:]).decode('utf8')
        cursor.execute(query)

    conn.commit()
    cursor.close()
