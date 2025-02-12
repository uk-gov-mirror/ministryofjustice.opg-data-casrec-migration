import json
import os
import logging
import time
from datetime import datetime

import colorlog as colourlog
from pythonjsonlogger import jsonlogger


class MyHandler(colourlog.StreamHandler):
    def __init__(self, env=None):
        self.env = env

        colourlog.StreamHandler.__init__(self)

        fmt = "%(log_color)s %(asctime)s %(filename)-18s %(levelname)-8s: %(message)s"

        fmt_date = "%Y-%m-%dT%T%Z"

        formatter = colourlog.ColoredFormatter(
            fmt,
            fmt_date,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "black,bg_green",
                "VERBOSE": "yellow",
                "DATA": "red",
            },
            secondary_log_colors={},
            style="%",
        )

        self.setFormatter(formatter)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def setup_logging(env, level=None):
    log = logging.getLogger("root")

    VERBOSE_LEVELV_NUM = 5
    logging.addLevelName(VERBOSE_LEVELV_NUM, "VERBOSE")

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE_LEVELV_NUM):
            self._log(VERBOSE_LEVELV_NUM, message, args, **kws)

    logging.Logger.verbose = verbose

    DATA_LEVELV_NUM = 5
    logging.addLevelName(DATA_LEVELV_NUM, "VERBOSE")

    def data(self, message, *args, **kws):
        if self.isEnabledFor(DATA_LEVELV_NUM):
            self._log(DATA_LEVELV_NUM, message, args, **kws)

    logging.Logger.data = data

    if env == "local":
        level = level if level else "VERBOSE"
        log.addHandler(MyHandler())
    else:
        level = "DEBUG"
        logHandler = logging.StreamHandler()
        formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        logHandler.setFormatter(formatter)
        log.addHandler(logHandler)
    log.setLevel(level)
    log.info(f"{level} logging enabled for environment {env}")

    return log
