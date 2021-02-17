from migration_steps.shared.table_helpers import (
    get_table_list,
    get_sequences_list,
    get_uid_sequences_list,
)

test_data = {
    "persons": {
        "sequences": [
            {"name": "persons_id_seq", "column": "id", "type": "pk"},
            {"name": "global_uid_seq", "column": "uid", "type": "uid"},
        ]
    },
    "addresses": {
        "sequences": [{"name": "addresses_id_seq", "column": "id", "type": "pk"}]
    },
    "phonenumbers": {
        "sequences": [{"name": "phonenumbers_id_seq", "column": "id", "type": "pk"}]
    },
    "cases": {
        "sequences": [
            {"name": "cases_id_seq", "column": "id", "type": "pk"},
            {"name": "global_uid_seq", "column": "uid", "type": "uid"},
        ]
    },
    "person_caseitem": {
        "sequences": [{"name": "person_caseitem_id_seq", "column": "id", "type": "pk"}]
    },
    "supervision_level_log": {
        "sequences": [
            {"name": "supervision_level_log_id_seq", "column": "id", "type": "pk"}
        ]
    },
}


def test_get_table_list():
    result = get_table_list(table_dict=test_data)
    assert result == [
        "persons",
        "addresses",
        "phonenumbers",
        "cases",
        "person_caseitem",
        "supervision_level_log",
    ]


def test_get_sequences_list():
    result = get_sequences_list(table_dict=test_data)
    assert result == [
        {"sequence_name": "persons_id_seq", "table": "persons", "column": "id"},
        {"sequence_name": "addresses_id_seq", "table": "addresses", "column": "id"},
        {
            "sequence_name": "phonenumbers_id_seq",
            "table": "phonenumbers",
            "column": "id",
        },
        {"sequence_name": "cases_id_seq", "table": "cases", "column": "id"},
        {
            "sequence_name": "person_caseitem_id_seq",
            "table": "person_caseitem",
            "column": "id",
        },
        {
            "sequence_name": "supervision_level_log_id_seq",
            "table": "supervision_level_log",
            "column": "id",
        },
    ]


def test_get_uid_sequences_list():
    result = get_uid_sequences_list(table_dict=test_data)
    assert result == [
        {
            "sequence_name": "global_uid_seq",
            "fields": [
                {"table": "persons", "column": "uid"},
                {"table": "cases", "column": "uid"},
            ],
        }
    ]
