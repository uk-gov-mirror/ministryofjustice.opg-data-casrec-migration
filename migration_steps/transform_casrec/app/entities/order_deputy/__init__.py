import logging

from entities.order_deputy.order_deputy import insert_order_deputy
from helpers import log_title

log = logging.getLogger("root")


def runner(config, target_db):
    """
    | Name                  | Running Order | Requires          |
    | --------------------- | ------------- | ----------------- |
    | order_deputy          | 1             | deputies, cases   |
    |                       |               |                   |

    """

    log.info(log_title(message="order_deputy"))

    log.debug("insert_order_deputy")
    insert_order_deputy(config, target_db)


if __name__ == "__main__":
    runner()
