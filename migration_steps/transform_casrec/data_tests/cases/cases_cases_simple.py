from pytest_cases import case

from data_tests.helpers import get_lookup_dict

module_name = "cases"
source_table = "order"
destination_table = "cases"


@case(tags="simple")
def case_cases_1(get_config):
    simple_matches = {}
    merge_columns = {"source": "Case", "transformed": "caserecnumber"}

    config = get_config

    source_columns = [f'"{x}"' for x in simple_matches.keys()]
    transformed_columns = [f'"{y}"' for x in simple_matches.values() for y in x]

    source_query = f"""
        SELECT
            "{merge_columns['source']}",
            {', '.join(source_columns)}
        FROM {config.etl1_schema}.{source_table}
    """

    transformed_query = f"""
        SELECT
            {merge_columns['transformed']},
            {', '.join(transformed_columns)}
        FROM {config.etl2_schema}.{destination_table}
    """

    return (simple_matches, merge_columns, source_query, transformed_query, module_name)


@case(tags="default")
def case_cases_2(get_config):
    defaults = {}

    config = get_config
    source_columns = [f'"{x}"' for x in defaults.keys()]

    source_query = f"""
        SELECT
            {', '.join(source_columns)}
        FROM {config.etl2_schema}.{destination_table}
    """

    return (defaults, source_query, module_name)


@case(tags="lookups")
# title is commented out because the anon data is wrong so it will never pass
def case_casess_3(get_config):

    lookup_fields = {}
    merge_columns = {"source": "Case", "transformed": "caserecnumber"}

    config = get_config

    source_columns = [f'"{x}"' for x in lookup_fields.keys()]
    transformed_columns = [f'"{y}"' for x in lookup_fields.values() for y in x]

    source_query = f"""
        SELECT
            "{merge_columns['source']}",
            {', '.join(source_columns)}
        FROM {config.etl1_schema}.{source_table}
    """

    transformed_query = f"""
        SELECT
            {merge_columns['transformed']},
            {', '.join(transformed_columns)}
        FROM {config.etl2_schema}.{destination_table}
    """

    return (lookup_fields, merge_columns, source_query, transformed_query, module_name)
