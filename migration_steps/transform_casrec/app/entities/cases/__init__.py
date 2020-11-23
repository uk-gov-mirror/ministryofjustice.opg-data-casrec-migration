import logging

from entities.cases.cases import insert_cases
from entities.cases.person_caseitem import insert_person_caseitem
from entities.cases.supervision_level_log import insert_supervision_level_log
from utilities.helpers import log_title

log = logging.getLogger("root")


def runner(config, etl2_db):
    """
    | Name      | Running Order | Requires |
    | --------- | ------------- | -------- |
    | cases     | 1             |          |
    |           |               |          |

    """

    log.info(log_title(message="cases"))

    log.debug("insert_cases")
    insert_cases(config, etl2_db)

    log.debug("insert_supervision_level_log")
    insert_supervision_level_log(config, etl2_db)

    log.debug("insert_person_caseitem")
    insert_person_caseitem(config, etl2_db)


if __name__ == "__main__":
    runner()
