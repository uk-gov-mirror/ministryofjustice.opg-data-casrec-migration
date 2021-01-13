from pandas._testing import assert_frame_equal

from merge_helpers import merge_source_data_with_existing_data

import pandas as pd

source_data_dict = {
    "id": [1, 2, 3, 4, 5],
    "casrecnumber": ["C1", "C2", "C3", "C4", "C5"],
    "firstname": ["Alan", "brian", "Colin", "Derek", "Eugene"],
    "surname": ["Alanson", "Brianson", "Colinson", "Derekson", "Eugeneson"],
    "test_notes": [
        "full match",
        "case mismatch",
        "casrecnumber mismatch",
        "all fields mismatch",
        "full match",
    ],
}


existing_data_dict = {
    "id": [1001, 1002, 1003, 1004, 1005],
    "casrecnumber": ["C1", "C2", "C30", "C999", "C5"],
    "firstname": ["Alan", "Brian", "Colin", "Donal", "Eugene"],
    "surname": ["Alanson", "Brianson", "Colinson", "Donalson", "Eugeneson"],
}

expected_data_dict = {
    "id": [1, 2, 3, 4, 5],
    "casrecnumber": ["C1", "C2", "C3", "C4", "C5"],
    "firstname": ["Alan", "brian", "Colin", "Derek", "Eugene"],
    "surname": ["Alanson", "Brianson", "Colinson", "Derekson", "Eugeneson"],
    "sirius_id": [1001, 0, 0, 0, 1005],
    "method": ["UPDATE", "INSERT", "INSERT", "INSERT", "UPDATE"],
}


source_data = pd.DataFrame(
    source_data_dict, columns=[x for x in source_data_dict if x != "test_notes"]
)
existing_data = pd.DataFrame(
    existing_data_dict, columns=[x for x in existing_data_dict]
)
expected_data = pd.DataFrame(
    expected_data_dict, columns=[x for x in expected_data_dict]
)
match_columns = ["casrecnumber", "firstname", "surname"]


def test_merge_source_data_with_existing_data():

    result = merge_source_data_with_existing_data(
        source_data=source_data,
        existing_data=existing_data,
        match_columns=match_columns,
    )

    assert_frame_equal(result, expected_data)
