class LocalConfig():
    connection_string = "postgresql://casrec:casrec@0.0.0.0:6666/casrecmigration"  # pragma: allowlist secret
    etl1_schema = "etl1"
    etl2_schema = "etl2"
    etl3_schema = "etl3"


class LocalSiriusConfig():
    connection_string = "postgresql://api:api@0.0.0.0:5555/api"  # pragma: allowlist secret
    sirius_schema = "public"


class SiriusConfig():
    connection_string = "postgresql://api:api@0.0.0.0:5555/api"  # pragma: allowlist secret
    sirius_schema = "public"


def get_config(env="local"):
    if env == "local":
        config = LocalConfig()

    return config
