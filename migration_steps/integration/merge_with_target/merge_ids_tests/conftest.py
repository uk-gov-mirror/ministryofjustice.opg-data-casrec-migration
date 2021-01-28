import pytest

from migration_steps.integration.merge_with_target.app import merge_helpers

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


@pytest.fixture()
def mock_get_max_uid_from_sirius(monkeypatch):
    def mock_sirius_id(*args, **kwargs):
        print("using mock get_max_uid_from_sirius")
        return 700000009998

    monkeypatch.setattr(merge_helpers, "get_max_id_from_sirius", mock_sirius_id)
