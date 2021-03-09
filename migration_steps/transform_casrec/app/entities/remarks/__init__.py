import logging


from helpers import log_title

from entities.remarks.notes import insert_notes

log = logging.getLogger("root")


def runner(target_db, db_config):
    """
    | Name          | Running Order  | Requires     |
    | ------------- | -------------- | ------------ |
    | notes         | 1              |              |
    | caseitem_note | 2              | notes, cases |
    |               |                |              |

    """

    log.info(log_title(message="remarks"))

    log.debug("insert_notes")
    insert_notes(target_db=target_db, db_config=db_config)


if __name__ == "__main__":

    runner()
