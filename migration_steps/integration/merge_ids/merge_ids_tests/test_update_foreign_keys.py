import pandas as pd

from merge_helpers import update_foreign_keys
from pandas._testing import assert_frame_equal

table = "pirates"

pirate_data_dict = {
    "id": [11, 12, 13, 14, 15],
    "transformation_id": [1, 2, 3, 4, 5],
    "ship_id": [3, 2, 3, 4, 5],
    "name": ["Jack Sparrow", "Barbossa", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
    "method": ["INSERT", "INSERT", "INSERT", "INSERT", "INSERT"],
}

ship_data_dict = {"id": [33, 44, 55], "transformation_id": [3, 4, 5]}


pirate_data = pd.DataFrame(pirate_data_dict, columns=[x for x in pirate_data_dict])
ship_data = pd.DataFrame(ship_data_dict, columns=[x for x in ship_data_dict])


fk_details = {"parent_table": "ships", "parent_col": "id", "fk_col": "ship_id"}


expected_result_dict = {
    "id": [11, 13, 14, 15],
    "transformation_id": [1, 3, 4, 5],
    "transformation_ship_id": [3, 3, 4, 5],
    "name": ["Jack Sparrow", "Blackbeard", "Bootstrap Bill", "Davy Jones"],
    "method": ["INSERT", "INSERT", "INSERT", "INSERT"],
    "ship_id": [33, 33, 44, 55],
}

expected_result = pd.DataFrame(
    expected_result_dict, columns=[x for x in expected_result_dict]
)


def test_update_foreign_keys():
    result = update_foreign_keys(
        df=pirate_data, parent_df=ship_data, fk_details=fk_details
    )

    assert_frame_equal(result, expected_result)
