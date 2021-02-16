import logging

# from entities.deputies.addresses import insert_addresses_deputies
from entities.deputies.persons import insert_persons_deputies
from helpers import log_title

log = logging.getLogger("root")


def runner(target_db, db_config):
    """
    | Name      | Running Order | Requires |
    | --------- | ------------- | -------- |
    | persons   | 1             |          |
    | addresses | 2             | persons  |
    |           |               |          |

    """

    log.info(log_title(message="deputies"))

    log.debug("insert_persons_deputies")
    insert_persons_deputies(target_db=target_db, db_config=db_config)

    log.debug("insert_addresses_deputies")
    # insert_addresses_deputies(target_db=target_db, db_config=db_config)


if __name__ == "__main__":
    runner()
