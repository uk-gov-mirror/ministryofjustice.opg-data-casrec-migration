import pytest

from conftest import test_db_config
from merge_helpers import generate_select_query


@pytest.mark.parametrize(
    "schema, table, columns, expected_query",
    [
        (
            test_db_config["source_schema"],
            "persons",
            ["id", "caserecnumber", "firstname", "surname"],
            "SELECT id, caserecnumber, firstname, surname from source_schema.persons;",
        ),
        (
            test_db_config["target_schema"],
            "persons",
            ["caserecnumber", "firstname", "surname"],
            "SELECT caserecnumber, firstname, surname from target_schema.persons;",
        ),
    ],
)
def test_generate_select_query(schema, table, columns, expected_query):

    result = generate_select_query(schema=schema, columns=columns, table=table)

    assert result == expected_query
