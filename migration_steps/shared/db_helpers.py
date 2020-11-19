import os

def execute_sql_file(sql_path, filename, conn):
    cursor = conn.cursor()
    sql_file = open(sql_path / filename, 'r')
    cursor.execute(sql_file.read())
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
