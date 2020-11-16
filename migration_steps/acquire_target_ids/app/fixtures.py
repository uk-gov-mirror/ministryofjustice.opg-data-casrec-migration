import pandas as pd
from config import get_config, CasrecMigConfig, SiriusConfig, load_env_vars
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


def main():

    print("Loading 10 people into Sirius to simulate skeleton case data")
    persons_df["uid"] = list(range(max_person_uid+1,max_person_uid+11,1))


if __name__ == "__main__":
    t = time.process_time()

    if environment in ("local", "development"):
        main()
    else:
        print(f"This step is not designed to run on environment '{environment}'")

    print(f"Total time: {round(time.process_time() - t, 2)}")
