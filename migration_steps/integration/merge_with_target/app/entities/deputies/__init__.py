import logging

from entities.deputies import persons

log = logging.getLogger("root")

entity_name = "Deputies"


def merge_source_data(db_config, target_db):
    log.info(f"Entity: {entity_name}")
    log.info(" - Persons")
    persons.merge_source_into_target(db_config, target_db)
