import logging

from entities.client import persons, addresses, phonenumbers

log = logging.getLogger("root")

entity_name = "Client"


def merge_source_data(db_config, target_db):
    log.info(f"Entity: {entity_name}")
    log.info(" - Persons")
    persons.merge_source_into_target(db_config, target_db)

    log.info(" - Addresses")
    addresses.merge_source_into_target(db_config, target_db)

    log.info(" - Phone Numbers")
    phonenumbers.merge_source_into_target(db_config, target_db)
