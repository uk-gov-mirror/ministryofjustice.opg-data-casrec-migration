import logging

from entities.supervision_level import supervision_level

log = logging.getLogger("root")

entity_name = "Supervision Level"


def merge_source_data(db_config, target_db):
    log.info(f"Entity: {entity_name}")
    log.info(" - Supervision Level")
    supervision_level.merge_source_into_target(db_config, target_db)
