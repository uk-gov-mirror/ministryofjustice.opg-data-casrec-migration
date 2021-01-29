import pytest
from conftest import test_db_config
import pandas as pd
from pandas._testing import assert_frame_equal

from migration_steps.integration.merge_with_target.app.merge_helpers import (
    reindex_new_data,
)

table = "pirates"

test_data_dict = {
    "id": [x for x in range(1, 6)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
    "method": ["INSERT", "INSERT", "INSERT", "INSERT", "UPDATE"],
}

test_data = pd.DataFrame(test_data_dict, columns=[x for x in test_data_dict])


expected_result_dict = {
    "id": [x + 143 for x in range(1, 5)],
    "transformation_id": [x for x in range(1, 5)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill"],
    "method": ["INSERT", "INSERT", "INSERT", "INSERT"],
}

expected_result = pd.DataFrame(
    expected_result_dict, columns=[x for x in expected_result_dict]
)


def test_reindex_new_data(mock_get_max_id_from_sirius):
    result = reindex_new_data(db_config=test_db_config, df=test_data, table=table)

    assert_frame_equal(result, expected_result)
