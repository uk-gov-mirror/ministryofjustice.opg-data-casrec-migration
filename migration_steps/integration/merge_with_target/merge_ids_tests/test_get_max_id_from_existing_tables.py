from migration_steps.integration.merge_with_target.app.utilities.reindex_primary_keys import (
    get_max_pk_from_existing_tables_query,
)

test_table_details = {
    "persons": {
        "table_type": "data",
        "pk": "id",
        "fks": [],
        "sequences": [
            {"name": "persons_id_seq", "column": "id", "type": "pk"},
            {"name": "global_uid_seq", "column": "uid", "type": "uid"},
        ],
    },
    "addresses": {
        "pk": "id",
        "fks": ["person_id"],
        "table_type": "data",
        "sequences": [{"name": "addresses_id_seq", "column": "id", "type": "pk"}],
    },
}


def test_get_max_id_from_existing_tables():

    get_max_pk_from_existing_tables_query(
        db_schema="test", table_details=test_table_details
    )
