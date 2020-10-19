import os


class BaseConfig:
    mapping_document = "docs/mapping_doc.xlsx"
    verbose = False
    row_limit = None


class LocalConfig(BaseConfig):
    password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    name = os.environ["DB_NAME"]
    environment = os.environ["ENVIRONMENT"]

    connection_string = f"postgresql://casrec:{password}@{db_host}:{port}/{name}"  # pragma: allowlist secret
    etl1_schema = "etl1"
    etl2_schema = "etl2"


def get_config(env="local"):
    if env == "local":
        config = LocalConfig()

    return config
