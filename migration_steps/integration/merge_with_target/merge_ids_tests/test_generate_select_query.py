import pytest

from conftest import test_db_config
from merge_helpers import generate_select_query


@pytest.mark.parametrize(
    "schema, table, columns, where_clause, expected_query",
    [
        (
            test_db_config["source_schema"],
            "persons",
            ["id", "caserecnumber", "firstname", "surname"],
            None,
            "SELECT id, caserecnumber, firstname, surname from source_schema.persons;",
        ),
        (
            test_db_config["target_schema"],
            "persons",
            ["caserecnumber", "firstname", "surname"],
            None,
            "SELECT caserecnumber, firstname, surname from target_schema.persons;",
        ),
        (
            test_db_config["source_schema"],
            "persons",
            ["id", "caserecnumber", "firstname", "surname"],
            {"type": "actor_client"},
            "SELECT id, caserecnumber, firstname, surname from "
            "source_schema.persons WHERE type = 'actor_client';",
        ),
    ],
)
def test_generate_select_query(schema, table, columns, where_clause, expected_query):

    result = generate_select_query(
        schema=schema, columns=columns, table=table, where_clause=where_clause
    )

    assert result == expected_query
