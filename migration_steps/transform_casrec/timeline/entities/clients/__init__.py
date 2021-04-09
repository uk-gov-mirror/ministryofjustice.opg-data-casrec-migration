import logging

# from entities.clients.persons import insert_persons_clients_timeline
from entities.clients.persons import insert_persons_client_timeline
from helpers import log_title, check_entity_enabled

log = logging.getLogger("root")


def runner(db_config):
    """
    | Name      | Running Order | Requires |
    | --------- | ------------- | -------- |
    | persons   | 1             |          |
    | addresses | 2             | persons  |
    |           |               |          |

    """

    entity_name = "clients"
    # if not check_entity_enabled(entity_name):
    #     return False

    log.info(log_title(message=entity_name))

    log.debug("insert_persons_clients_timeline")
    insert_persons_client_timeline(
        db_config=db_config,
    )


if __name__ == "__main__":

    runner()
