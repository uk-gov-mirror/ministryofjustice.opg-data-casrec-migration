import pytest
from conftest import test_db_config

from merge_helpers import generate_max_id_query


@pytest.mark.parametrize(
    "schema, table, id, expected_result",
    [
        (
            test_db_config["source_schema"],
            "addresses",
            "cheese",
            "SELECT max(cheese) from source_schema.addresses;",
        ),
        (
            test_db_config["source_schema"],
            "pirates",
            None,
            "SELECT max(id) from source_schema.pirates;",
        ),
    ],
)
def test_generate_max_id_query(schema, table, id, expected_result):
    if id:
        result = generate_max_id_query(schema=schema, table=table, id=id)
    else:
        result = generate_max_id_query(schema=schema, table=table)

    assert result == expected_result
