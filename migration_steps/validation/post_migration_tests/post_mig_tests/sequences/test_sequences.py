import pytest

from checks import sequences

test_sequence = [
    {"sequence_name": "seq_no_match", "table": "table", "column": "column"},
    {"sequence_name": "seq_no_match_2", "table": "table", "column": "column"},
]


def test_check_sequences_fail(monkeypatch):
    expected_result = False

    def mock_get_max_value(*args, **kwargs):
        return 5

    monkeypatch.setattr(sequences, "get_max_value", mock_get_max_value)

    def mock_get_sequence_currval(*args, **kwargs):
        return 6

    monkeypatch.setattr(sequences, "get_sequence_currval", mock_get_sequence_currval)

    result = sequences.check_sequences(sequences=test_sequence, db_config={})

    assert result == expected_result


def test_check_sequences_pass(monkeypatch):
    expected_result = True

    def mock_get_max_value(*args, **kwargs):
        return 6

    monkeypatch.setattr(sequences, "get_max_value", mock_get_max_value)

    def mock_get_sequence_currval(*args, **kwargs):
        return 6

    monkeypatch.setattr(sequences, "get_sequence_currval", mock_get_sequence_currval)

    result = sequences.check_sequences(sequences=test_sequence, db_config={})

    assert result == expected_result
