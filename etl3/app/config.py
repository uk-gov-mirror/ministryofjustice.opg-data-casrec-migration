import os


class LocalConfig:
    password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    name = os.environ.get("DB_NAME")

    connection_string = f"postgresql://casrec:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret

    etl1_schema = "etl1"
    etl2_schema = "etl2"
    etl3_schema = "etl3"


class LocalSiriusConfig:
    password = os.environ.get("SIRIUS_DB_PASSWORD")
    db_host = os.environ.get("SIRIUS_DB_HOST")
    port = os.environ.get("SIRIUS_DB_PORT")
    name = os.environ.get("SIRIUS_DB_NAME")

    connection_string = f"postgresql://api:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret
    sirius_schema = "public"


class SiriusConfig:
    connection_string = (
        "postgresql://api:api@0.0.0.0:5555/api"  # pragma: allowlist secret
    )
    sirius_schema = "public"


def get_config(env="local"):
    if env == "local":
        config = LocalConfig()

    return config
