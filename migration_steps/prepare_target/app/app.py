import os
import time
import psycopg2
from config import get_config
from pathlib import Path
from dotenv import load_dotenv
from helpers import execute_sql_file, result_from_sql_file, execute_generated_sql

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
env_path = current_path / "../.env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)


def main():
    conn_target = psycopg2.connect(config.get_db_connection_string("target"))

    # operations which need to be performed on Sirius DB ahead of the final Casrec Migration
    execute_sql_file('prepare_sirius.sql', conn_target)

    # roll back previous migration
    max_orig_person_id = result_from_sql_file('get_max_orig_person_id.sql', conn_target)
    execute_generated_sql(
        'rollback_fixtures.template.sql',
        '{max_orig_person_id}',
        max_orig_person_id,
        conn_target
    )

    conn_target.close()


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
