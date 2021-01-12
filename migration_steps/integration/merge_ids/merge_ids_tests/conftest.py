import pytest

import merge_helpers

test_db_config = {
    "db_connection_string": "db_connection_string",
    "source_schema": "source_schema",
    "target_schema": "target_schema",
}


@pytest.fixture()
def mock_get_max_id_from_sirius(monkeypatch):
    def mock_sirius_id(*args, **kwargs):
        print("using mock get_max_id_from_sirius")
        return 143

    monkeypatch.setattr(merge_helpers, "get_max_id_from_sirius", mock_sirius_id)
