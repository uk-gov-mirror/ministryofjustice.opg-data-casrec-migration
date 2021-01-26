import pytest

from migration_steps.integration.merge_with_target.app.utilities.generate_luhn_checksum import (
    double_alternate_digits,
    sum_big_digits,
    sum_all_digits,
    multiply_by_9_and_return_unit,
    generate_luhn_checksum,
    append_checksum,
)


@pytest.mark.parametrize(
    "test_number, expected_result",
    [
        ([3, 8, 4, 3, 2, 9, 6], [6, 8, 8, 3, 4, 9, 12]),
        ([2, 8, 6, 9, 4, 7], [2, 16, 6, 18, 4, 14]),
        ([3, 7, 5, 6, 2, 1, 9, 8, 6, 7], [3, 14, 5, 12, 2, 2, 9, 16, 6, 14]),
    ],
)
def test_double_alternate_digits(test_number, expected_result):
    result = double_alternate_digits(list_of_digits=test_number)

    assert result == expected_result


@pytest.mark.parametrize(
    "test_number, expected_result",
    [
        ([6, 8, 8, 3, 4, 9, 12], [6, 8, 8, 3, 4, 9, 3]),
        ([2, 16, 6, 18, 4, 14], [2, 7, 6, 9, 4, 5]),
        ([3, 14, 5, 12, 2, 2, 9, 16, 6, 14], [3, 5, 5, 3, 2, 2, 9, 7, 6, 5]),
    ],
)
def test_sum_big_digits(test_number, expected_result):
    result = sum_big_digits(list_of_digits=test_number)

    assert result == expected_result


@pytest.mark.parametrize(
    "test_number, expected_result",
    [
        ([6, 8, 8, 3, 4, 9, 3], 41),
        ([2, 7, 6, 9, 4, 5], 33),
        ([3, 5, 5, 3, 2, 2, 9, 7, 6, 5], 47),
    ],
)
def test_sum_all_digits(test_number, expected_result):
    result = sum_all_digits(list_of_digits=test_number)

    assert result == expected_result


@pytest.mark.parametrize("test_number, expected_result", [(41, 9), (33, 7), (47, 3)])
def test_multiply_by_9_and_return_unit(test_number, expected_result):
    result = multiply_by_9_and_return_unit(number=test_number)

    assert result == expected_result


@pytest.mark.parametrize(
    "test_number, expected_result", [(3843296, 9), (286947, 7), (3756219867, 3)]
)
def test_add_luhn_checksum(test_number, expected_result):
    result = generate_luhn_checksum(original_number=test_number)

    assert result == expected_result


@pytest.mark.parametrize(
    "test_number, expected_result",
    [
        (3843296, 38432969),
        (286947, 2869477),
        (3756219867, 37562198673),
        (70000000999, 700000009998),
    ],
)
def test_append_checksum(test_number, expected_result):
    result = append_checksum(original_number=test_number)

    assert result == expected_result
