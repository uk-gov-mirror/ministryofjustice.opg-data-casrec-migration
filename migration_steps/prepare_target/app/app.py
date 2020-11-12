import os
import time
import psycopg2
from config import get_config
from pathlib import Path
from dotenv import load_dotenv

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sql_path = current_path / 'sql'


def load_env_vars():
    env_path = current_path / "../.env"
    load_dotenv(dotenv_path=env_path)


load_env_vars()
environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)


def execute_sql_file(filename, conn, return_cursor=False):
    cursor = conn.cursor()
    sql_file = open(sql_path / filename, 'r')
    cursor.execute(sql_file.read())
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


def execute_sql_from_template(template_filename, search, replace, conn):
    sql_filename = template_filename.replace("template.", "")
    create_from_template(template_filename, sql_filename, search, replace)
    execute_sql_file(sql_path / sql_filename, conn)
    os.remove(sql_path / sql_filename)


def main():
    conn = psycopg2.connect(config.get_db_connection_string("target"))

    # operations which need to be performed on Sirius DB ahead of the final Casrec Migration
    execute_sql_file('prepare_sirius.sql', conn)

    # roll back previous migration
    cursor = execute_sql_file('get_max_orig_person_id.sql', conn, True)
    max_orig_person_id = cursor.fetchone()[0]
    execute_sql_from_template(
        'rollback_fixtures.template.sql',
        '{max_orig_person_id}',
        max_orig_person_id,
        conn
    )


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
