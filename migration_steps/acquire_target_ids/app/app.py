import os
import time
import psycopg2
from config import get_config
from pathlib import Path
from dotenv import load_dotenv
from helpers import *
import pandas as pd

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sql_path = current_path / 'sql'
env_path = current_path / "../.env"
load_dotenv(dotenv_path=env_path)

environment = os.environ.get("ENVIRONMENT")
config = get_config(environment)


def main():
    conn_migration = psycopg2.connect(config.get_db_connection_string("migration"))
    conn_target = psycopg2.connect(config.get_db_connection_string("target"))

    # add columns which will take corresponding sirius ids
    execute_sql_file('sirius_id_cols.sql', conn_migration)

    print("Fetching Sirius IDs...")

    print("- Clients")
    sql_file = open(sql_path / 'select_sirius_clients.sql', 'r')
    sirius_persons_df = pd.read_sql_query(sql_file.read(), con=conn_target, index_col=None)
    execute_mogrify(conn_migration, sirius_persons_df, 'sirius_map_persons')

    # print("- Cases")
    # sirius_cases = pd.read_sql_table("cases", con=sirius_db_engine)
    # sirius_cases_keys = sirius_cases[(sirius_cases.casetype == "ORDER")][
    #     ["id", "caserecnumber", "client_id", "casesubtype", "orderdate"]
    # ]
    # sirius_cases_keys.columns = [
    #     "sirius_cases_id",
    #     "sirius_cases_caserecnumber",
    #     "sirius_persons_id",
    #     "sirius_casesubtype",
    #     "orderdate",
    # ]
    # sirius_cases_keys.to_sql(
    #     "sirius_map_cases",
    #     con=etl3_db_engine,
    #     schema=CasrecMigConfig.pre_migrate_schema,
    #     if_exists="replace",
    #     index=False,
    #     dtype={"sirius_persons_id": Integer},
    # )
    # print(sirius_cases_keys)

    # print("- Addresses")
    # sirius_addresses = pd.read_sql_table("addresses", con=sirius_db_engine)
    # sirius_addresses_keys = sirius_addresses[["id", "person_id"]]
    # sirius_addresses_keys.columns = ["sirius_addresses_id", "sirius_persons_id"]
    # sirius_addresses_keys.to_sql(
    #     "sirius_map_addresses",
    #     con=etl3_db_engine,
    #     schema=CasrecMigConfig.pre_migrate_schema,
    #     if_exists="replace",
    #     index=False,
    # )
    #
    # print("Update main entities with sirius IDs from map entities...")
    # print("- Persons")
    # sql = """UPDATE etl3.persons persons
    # SET sirius_id = map.sirius_persons_id
    # FROM etl3.sirius_map_persons map
    # WHERE map.caserecnumber = persons.caserecnumber"""
    # etl3_db_engine.execute(sql)

    # print("- Cases & person_caseitem")
    # # anything other than 2 = pfa (CHECK THIS)
    # # 2 = hw
    # sql = """UPDATE etl3.cases cases
    # SET ordersubtype = 'hw'
    # WHERE ordersubtype = '2';
    # UPDATE etl3.sirius_map_cases SET sirius_casesubtype = 'hw' WHERE sirius_casesubtype = '2'"""
    # etl3_db_engine.execute(sql)
    # sql = """UPDATE etl3.cases cases
    # SET ordersubtype = 'pfa'
    # WHERE ordersubtype != 'hw';
    # UPDATE etl3.sirius_map_cases
    # SET sirius_casesubtype = 'pfa'
    # WHERE sirius_casesubtype != 'hw'"""
    # etl3_db_engine.execute(sql)
    #
    # sql = """UPDATE etl3.person_caseitem
    # SET sirius_person_id = persons.sirius_id
    # FROM etl3.persons WHERE persons.id = CAST(person_caseitem.person_id AS INTEGER)"""
    # etl3_db_engine.execute(sql)
    # sql = """UPDATE etl3.cases cases
    # SET sirius_id = map.sirius_cases_id
    # FROM etl3.person_caseitem, etl3.sirius_map_cases map
    # WHERE CAST(person_caseitem.case_id AS INTEGER) = cases.id
    # AND map.sirius_persons_id = person_caseitem.sirius_person_id
    # AND map.sirius_casesubtype = cases.ordersubtype"""
    # etl3_db_engine.execute(sql)
    # sql = """UPDATE etl3.person_caseitem
    # SET sirius_case_id = etl3.cases.sirius_id
    # FROM etl3.cases WHERE cases.id = CAST(person_caseitem.case_id AS INTEGER)"""
    # etl3_db_engine.execute(sql)
    # sql = """UPDATE etl3.cases cases
    # SET sirius_client_id = map.sirius_persons_id
    # FROM etl3.sirius_map_cases map WHERE map.sirius_cases_id = cases.sirius_id"""
    # etl3_db_engine.execute(sql)

    # print("- Addresses")
    # sql = """UPDATE etl3.addresses
    # SET sirius_id = map.sirius_addresses_id
    # FROM etl3.persons persons, etl3.sirius_map_addresses map
    # WHERE persons.id = CAST(addresses.person_id AS INTEGER)
    # AND map.sirius_persons_id = persons.sirius_id"""
    # etl3_db_engine.execute(sql)
    # sql = """UPDATE etl3.addresses
    # SET sirius_person_id = persons.sirius_id
    # FROM etl3.persons persons WHERE persons.id = CAST(addresses.person_id AS INTEGER)"""
    # etl3_db_engine.execute(sql)

    # print("- Notes")
    # sql = """UPDATE etl3.person_note
    # SET sirius_person_id = persons.sirius_id
    # FROM etl3.persons WHERE persons.id = CAST(person_note.person_id AS INTEGER)"""
    # etl3_db_engine.execute(sql)


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
