import os
import logging
from pathlib import Path
from dotenv import load_dotenv


def load_env_vars():
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    env_path = current_path / "../.env"
    load_dotenv(dotenv_path=env_path)


class BaseConfig:
    load_env_vars()
    db_config = {
        "migration": {
            "host": os.environ.get("DB_HOST"),
            "port": os.environ.get("DB_PORT"),
            "name": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD")
        },
        "target": {
            "host": os.environ.get("SIRIUS_DB_HOST"),
            "port": os.environ.get("SIRIUS_DB_PORT"),
            "name": os.environ.get("SIRIUS_DB_NAME"),
            "user": os.environ.get("SIRIUS_DB_USER"),
            "password": os.environ.get("SIRIUS_DB_PASSWORD")
        }
    }

    row_limit = 5

    INFO = 0
    DEBUG = 1
    VERBOSE = 2
    DATA = 3
    CRITICAL = 4
    verbosity_levels = {0: "INFO", 1: "DEBUG", 2: "VERBOSE", 3: "DATA", 4: "CRITICAL"}

    def verbose(self, msg, *args, **kwargs):
        if logging.getLogger().isEnabledFor(self.VERBOSE):
            logging.log(self.VERBOSE, msg)

    def critical(self, msg, *args, **kwargs):
        if logging.getLogger().isEnabledFor(self.CRITICAL):
            logging.log(self.CRITICAL, msg)

    def custom_log_level(self):
        logging.addLevelName(self.VERBOSE, "VERBOSE")
        logging.Logger.verbose = self.verbose

        logging.addLevelName(self.CRITICAL, "CRITICAL")
        logging.Logger.critical = self.critical

    def get_db_connection_string(self, db):
        return f"postgresql://{self.db_config[db]['user']}:{self.db_config[db]['password']}@" \
               f"{self.db_config[db]['host']}:{self.db_config[db]['port']}" \
               f"/{self.db_config[db]['name']}"  # pragma: allowlist secret


class LocalConfig(BaseConfig):
    verbosity_levels = {0: "INFO", 1: "DEBUG", 2: "VERBOSE", 3: "DATA"}

    def data(self, msg, *args, **kwargs):
        if logging.getLogger().isEnabledFor(self.DATA):
            logging.log(self.DATA, msg)

    def custom_log_level(self):
        logging.addLevelName(self.VERBOSE, "VERBOSE")
        logging.Logger.verbose = self.verbose

        logging.addLevelName(self.DATA, "DATA")
        logging.Logger.data = self.data


def get_config(env="local"):
    if env == "local":
        config = LocalConfig()
    else:
        config = BaseConfig()
    return config
