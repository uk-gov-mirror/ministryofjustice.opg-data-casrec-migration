from datetime import datetime

from pytest_cases import case

module_name = "client_phonenumbers"
source_table = "pat"
destination_table = "phonenumbers"


@case(tags="simple")
def case_clients_phonenos_1(get_config):
    simple_matches = {
        "Client Phone": ["phone_number"],
    }
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
def case_clients_phonenos_2(get_config):
    defaults = {
        "type": "Home",
        "is_default": False,
        # "updateddate": "Todays Date",
    }

    config = get_config
    source_columns = [f'"{x}"' for x in defaults.keys()]

    source_query = f"""
        SELECT
            {', '.join(source_columns)}
        FROM {config.etl2_schema}.{destination_table}
    """

    return (defaults, source_query, module_name)


@case(tags="calculated")
def case_clients_phonenos_3(get_config):
    today = datetime.today().strftime("%Y-%m-%d")

    calculated_fields = {
        "updateddate": today,
    }

    config = get_config
    source_columns = [f'"{x}"' for x in calculated_fields.keys()]

    source_query = f"""
        SELECT
            {', '.join(source_columns)}
        FROM {config.etl2_schema}.{destination_table}
    """

    return (calculated_fields, source_query, module_name)


@case(tags="one_to_one_joins")
def case_clients_phonenos_joins(get_config):
    join_columns = {
        "person_id": {"persons": "id"},
    }
    merge_columns = {"fk_child": "c_case", "fk_parent": "caserecnumber"}

    config = get_config

    fk_child_col = [f'"{k}"' for k in join_columns.keys()]

    parent_table = [y for x in join_columns.values() for y in x]

    fk_parent_col = [f'"{y}"' for x in join_columns.values() for y in x.values()]

    fk_child_query = f"""
        SELECT
            "{merge_columns['fk_child']}",
            {', '.join(fk_child_col)}
        FROM {config.etl2_schema}.{destination_table}
    """

    fk_parent_query = f"""
            SELECT
                "{merge_columns['fk_parent']}",
                {', '.join(fk_parent_col)}
            FROM {config.etl2_schema}.{parent_table[0]}
        """

    return (join_columns, merge_columns, fk_child_query, fk_parent_query, module_name)
