import pandas as pd
from sqlalchemy import create_engine
from config import get_config, CasrecMigConfig, SiriusConfig, load_env_vars
from sqlalchemy.types import (
    Integer,
    Text,
    String,
    Date,
    DateTime,
    BigInteger,
    TIMESTAMP,
    Boolean,
    JSON,
)
import json
import os
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

migration_db_engine = create_engine(CasrecMigConfig.connection_string)
sirius_db_engine = create_engine(SiriusConfig.connection_string)


def main():
    sql = "SELECT MAX(uid) FROM persons"
    max_person_uid = get_single_sql_value(sirius_db_engine, sql)

    sql = "UPDATE etl3.persons SET sirius_id = null WHERE sirius_id IS NOT NULL; "
    migration_db_engine.execute(sql)

    print("Loading 10 people into Sirius to simulate skeleton case data")
    sql = (
        "SELECT "
        "firstname, CONCAT(surname, ' (LIVELINK SKELETON)') as surname, "
        "type, caserecnumber "
        "FROM etl3.persons "
        "WHERE sirius_id IS NULL "
        "ORDER BY id ASC LIMIT 10"
    )
    persons_df = pd.read_sql_query(sql, con=migration_db_engine, index_col=None)
    persons_df["correspondencebypost"] = 0
    persons_df["correspondencebyphone"] = 0
    persons_df["correspondencebyemail"] = 0
    persons_df["clientsource"] = "SKELETON"
    persons_df["supervisioncaseowner_id"] = 10
    persons_df["uid"] = list(range(max_person_uid+1,max_person_uid+11,1))
    print(persons_df)

    persons_df.to_sql(
        "persons",
        sirius_db_engine,
        if_exists="append",
        index=False,
        chunksize=500,
        dtype={
            "firstname": String(255),
            "surname": String(255),
            "createddate": TIMESTAMP(),
            "type": String(255),
            "caserecnumber": String(255),
            "correspondencebypost": Boolean,
            "correspondencebyphone": Boolean,
            "correspondencebyemail": Boolean,
            "uid": BigInteger,
            "clientsource": String(255),
            "supervisioncaseowner_id": Integer,
        },
    )

    print("- Associated addresses")
    sql = "SELECT id FROM persons ORDER BY id DESC LIMIT 10"
    addresses_df = pd.read_sql_query(sql, con=sirius_db_engine, index_col=None)
    addresses_df = addresses_df.sort_values(by=["id"])
    addresses_df = addresses_df.rename(columns={"id": "person_id"})
    addresses_df["isairmailrequired"] = False
    print(addresses_df)
    addresses_df.to_sql(
        "addresses",
        sirius_db_engine,
        if_exists="append",
        index=False,
        dtype={"person_id": Integer, "isairmailrequired": Boolean},
    )
    default_address = json.dumps(["", "", ""], separators=(",", ", "))
    sql = f"UPDATE addresses SET address_lines = '{default_address}' WHERE person_id > {max_orig_person_id}"
    sirius_db_engine.execute(sql)

    # print("- Associated cases")
    # sql = "SELECT id, caserecnumber FROM persons ORDER BY id DESC LIMIT 10"
    # persons_fixtures = pd.read_sql_query(sql, con=sirius_db_engine, index_col=None)
    #
    # sql = """
    # SELECT *
    # FROM etl3.cases
    # WHERE caserecnumber
    # IN (SELECT caserecnumber FROM etl3.persons ORDER BY id ASC LIMIT 5)
    # """
    # etl_cases_df = pd.read_sql_query(sql, con=migration_db_engine, index_col=None)
    #
    # cases_df = etl_cases_df.merge(
    #     persons_fixtures,
    #     how="left",
    #     left_on="caserecnumber",
    #     right_on="caserecnumber",
    #     suffixes=["_case", "_person"],
    # )
    #
    # print(etl_cases_df)
    #
    # cases_df = cases_df.drop(
    #     ["id_case", "c_order_no", "sirius_id", "sirius_client_id"], axis=1
    # )
    # cases_df = cases_df.rename(columns={"id_person": "client_id"})
    # cases_df = cases_df.rename(columns={"ordersubtype": "casesubtype"})
    # cases_df["casetype"] = cases_df["type"].str.upper()
    # print(cases_df)
    #
    # cases_df.to_sql(
    #     "cases",
    #     sirius_db_engine,
    #     if_exists="append",
    #     index=False,
    #     dtype={
    #         "orderdate": Date,
    #         "orderissuedate": Date,
    #         "orderexpirydate": Date,
    #         "statusdate": Date,
    #         "caserecnumber": String(255),
    #         "ordersubtype": String(255),
    #         "uid": BigInteger,
    #         "casetype": String(255),
    #         "client_id": Integer,
    #     },
    # )

    # sql = """
    # SELECT client_id, id
    # FROM cases WHERE caserecnumber IN
    # (SELECT caserecnumber FROM persons ORDER BY id DESC LIMIT 5)
    # """
    # person_caseitems_df = etl_cases_df = pd.read_sql_query(
    #     sql, con=sirius_db_engine, index_col=None
    # )
    # person_caseitems_df = person_caseitems_df.rename(columns={"client_id": "person_id"})
    # person_caseitems_df = person_caseitems_df.rename(columns={"id": "caseitem_id"})
    # person_caseitems_df.to_sql(
    #     "person_caseitem",
    #     sirius_db_engine,
    #     if_exists="append",
    #     index=False,
    #     dtype={"person_id": Integer, "case_id": Integer},
    # )


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
