import os
import time
import psycopg2
from config import get_config
from pathlib import Path
from dotenv import load_dotenv
from entities import client
from entities import address

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sql_path = current_path / 'sql'
env_path = current_path / "../.env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)


def main():
    conn_migration = psycopg2.connect(config.get_db_connection_string("migration"))
    conn_target = psycopg2.connect(config.get_db_connection_string("target"))

    print("Fetch matching IDs from target (Sirius)")
    client.fetch_target_ids(config, conn_migration, conn_target)
    address.fetch_target_ids(config, conn_migration, conn_target)

    print("Merge target IDs in with pre_migrate data")
    client.merge_target_ids(config, conn_migration, conn_target)
    address.merge_target_ids(config, conn_migration, conn_target)


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
