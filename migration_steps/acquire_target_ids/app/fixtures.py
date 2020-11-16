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

    print("Loading 10 people into Sirius to simulate skeleton case data")
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
    addresses_df.to_sql(
        "addresses",
        sirius_db_engine,
        if_exists="append",
        index=False,
        dtype={"person_id": Integer, "isairmailrequired": Boolean},
    )


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
