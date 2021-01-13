import logging

from entities.cases import cases, person_caseitem

log = logging.getLogger("root")

entity_name = "Case"


def merge_source_data(db_config, target_db):
    log.info(f"Entity: {entity_name}")
    log.info(" - Case")
    cases.merge_source_into_target(db_config, target_db)

    log.info(" - Person CaseItem")
    person_caseitem.merge_source_into_target(db_config, target_db)
