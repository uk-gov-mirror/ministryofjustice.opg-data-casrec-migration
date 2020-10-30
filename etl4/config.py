import os


class CasrecMigConfig:
    password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    name = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")

    connection_string = f"postgresql://{user}:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret

    etl1_schema = "load_casrec"
    etl2_schema = "transform_casrec"
    etl3_schema = "acquire_target_ids"


class SiriusConfig:
    password = os.environ.get("SIRIUS_DB_PASSWORD")
    db_host = os.environ.get("SIRIUS_DB_HOST")
    port = os.environ.get("SIRIUS_DB_PORT")
    name = os.environ.get("SIRIUS_DB_NAME")
    user = os.environ.get("SIRIUS_DB_USER")

    connection_string = f"postgresql://{user}:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret
    sirius_schema = "public"


def get_config(env="local"):
    if env == "local":
        config = CasrecMigConfig()

    return config
