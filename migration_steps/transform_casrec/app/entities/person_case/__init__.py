import logging

from entities.cases.person_caseitem import insert_person_caseitem
from helpers import log_title

log = logging.getLogger("root")


def runner(config, target_db):
    """
    | Name                  | Running Order | Requires          |
    | --------------------- | ------------- | ----------------- |
    | person_caseitem       | 1             | persons, cases    |
    |                       |               |                   |

    """

    log.info(log_title(message="person_case"))

    log.debug("insert_person_caseitem")
    insert_person_caseitem(config, target_db)


if __name__ == "__main__":
    runner()
