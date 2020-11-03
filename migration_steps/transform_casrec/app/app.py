import time
import os

from sqlalchemy import create_engine
import click

from utilities.clear_database import clear_tables
from utilities.db_insert import InsertData
from entities.cases.cases import insert_cases
from entities.clients.addresses import insert_addresses_clients
from entities.clients.persons import insert_persons_clients
from entities.deputies.addresses import insert_addresses_deputies

from entities.deputies.persons import insert_persons_deputies
from entities.notes.notes import insert_notes
from entities.notes.persons_note import insert_person_notes
from entities.person_case.order_deputy import insert_order_deputy
from entities.person_case.person_caseitem import insert_person_caseitem
from config import LocalConfig, get_config
from pathlib import Path
from dotenv import load_dotenv


current_path = Path(os.path.dirname(os.path.realpath(__file__)))
env_path = current_path / ".env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")

config = get_config(env=environment)

etl2_db_engine = create_engine(config.connection_string)

etl2_db = InsertData(
    db_engine=etl2_db_engine, schema=config.etl2_schema, is_verbose=True
)


@click.command()
@click.option("--clear", prompt=False, default=False)
def main(clear):

    if clear:
        clear_tables(config)

    # Clients - personal details
    insert_persons_clients(config, etl2_db)
    insert_addresses_clients(config, etl2_db)

    # Deputies - personal details
    insert_persons_deputies(config, etl2_db)
    insert_addresses_deputies(config, etl2_db)

    # Cases
    insert_cases(config, etl2_db)

    # Join Persons to Cases
    insert_person_caseitem(config, etl2_db)
    insert_order_deputy(config, etl2_db)

    # Notes
    insert_notes(config, etl2_db)

    # Join Notes to Persons
    insert_person_notes(config, etl2_db)


if __name__ == "__main__":
    t = time.process_time()

    main()

    print(f"Total time: {round(time.process_time() - t, 2)}")
