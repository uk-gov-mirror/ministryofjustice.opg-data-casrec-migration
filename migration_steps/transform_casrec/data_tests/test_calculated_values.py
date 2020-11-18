from pytest_cases import parametrize_with_cases

from data_tests.conftest import (
    list_of_test_cases,
    SAMPLE_PERCENTAGE,
    add_to_tested_list,
)
from data_tests.helpers import get_data_from_query


@parametrize_with_cases(
    ("calculated_fields", "source_query", "module_name"),
    cases=list_of_test_cases,
    has_tag="calculated",
)
def test_default_values(get_config, calculated_fields, source_query, module_name):

    # print(f"source_query: {source_query}")

    config = get_config

    add_to_tested_list(
        module_name=module_name, tested_fields=[x for x in calculated_fields.keys()]
    )

    source_sample_df = get_data_from_query(
        query=source_query, config=config, sample=True
    )

    # print(source_sample_df.to_markdown())

    assert source_sample_df.shape[0] > 0

    print(f"Checking {source_sample_df.shape[0]} rows of data ({SAMPLE_PERCENTAGE}%) ")
    assert source_sample_df.shape[0] > 0
    for k, v in calculated_fields.items():
        matches = source_sample_df[k].str.contains(str(v))
        total_matches = matches.sum()
        success = total_matches == source_sample_df.shape[0]
        print(f"checking {k} == {v}.... {'OK' if success else 'oh no'} ")
        assert success
