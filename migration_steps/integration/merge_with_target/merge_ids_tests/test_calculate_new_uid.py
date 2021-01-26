import pytest
from conftest import test_db_config
import pandas as pd
from pandas._testing import assert_frame_equal

from migration_steps.integration.merge_with_target.app.merge_helpers import (
    calculate_new_uid,
)

table = "pirates"

test_data_dict = {
    "id": [x for x in range(1, 6)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
}

test_data = pd.DataFrame(test_data_dict, columns=[x for x in test_data_dict])


expected_result_dict = {
    "id": [x for x in range(1, 6)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
    "uid": [700000009998, 700000010004, 700000010012, 700000010020, 700000010038],
}

expected_result = pd.DataFrame(
    expected_result_dict, columns=[x for x in expected_result_dict]
)


def test_calculate_new_uid(mock_get_max_uid_from_sirius):
    result = calculate_new_uid(
        db_config=test_db_config, df=test_data, table=table, column_name="uid"
    )

    assert_frame_equal(result, expected_result)
