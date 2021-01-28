import pandas as pd
from pandas._testing import assert_frame_equal

from merge_helpers import reindex_existing_data

table = "pirates"

test_data_dict = {
    "id": [x for x in range(1, 6)],
    "sirius_id": [x for x in range(11, 16)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
    "method": ["UPDATE", "UPDATE", "UPDATE", "UPDATE", "INSERT"],
}

test_data = pd.DataFrame(test_data_dict, columns=[x for x in test_data_dict])


expected_result_dict = {
    "transformation_id": [x for x in range(1, 5)],
    "sirius_id": [x for x in range(11, 15)],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill"],
    "method": ["UPDATE", "UPDATE", "UPDATE", "UPDATE"],
    "id": [x for x in range(11, 15)],
}

expected_result = pd.DataFrame(
    expected_result_dict, columns=[x for x in expected_result_dict]
)


def test_reindex_existing_data():
    result = reindex_existing_data(df=test_data, table=table)

    assert_frame_equal(result, expected_result)
