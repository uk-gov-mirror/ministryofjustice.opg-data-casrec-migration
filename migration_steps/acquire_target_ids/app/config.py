import os
from pathlib import Path
from dotenv import load_dotenv


def get_config(env="local"):
    if env == "local":
        config = CasrecMigConfig()

    return config


def load_env_vars():
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    env_path = current_path / "../.env"
    load_dotenv(dotenv_path=env_path)


class CasrecMigConfig:
    load_env_vars()
    password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    name = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")

    connection_string = f"postgresql://{user}:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret

    etl1_schema = "etl1"
    etl2_schema = "etl2"
    etl3_schema = "etl3"


class SiriusConfig:
    load_env_vars()
    password = os.environ.get("SIRIUS_DB_PASSWORD")
    db_host = os.environ.get("SIRIUS_DB_HOST")
    port = os.environ.get("SIRIUS_DB_PORT")
    name = os.environ.get("SIRIUS_DB_NAME")
    user = os.environ.get("SIRIUS_DB_USER")

    connection_string = f"postgresql://{user}:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret
    sirius_schema = "public"
