import pandas as pd
import pytest
from pytest_cases import case


module_name = "client_persons"
source_table = "deputy"
destination_table = "persons"
destination_condition = "WHERE type = 'actor_deputy'"


@case(tags="simple")
def case_deputies_1(test_config):
    simple_matches = {
        "Dep Forename": ["firstname"],
        "Dep Surname": ["surname"],
        # "Email": ['email'], # can't test as it's also the merge col
        # "AKA Name": ['othernames'], # marked as `not mapped`
        # "Mobile": ['mobilenumber'] # marked as `not mapped`
    }
    merge_columns = {"source": "Email", "transformed": "email"}

    config = test_config

    source_columns = [f'"{x}"' for x in simple_matches.keys()]
    transformed_columns = [f'"{y}"' for x in simple_matches.values() for y in x]

    source_query = f"""
        SELECT
            "{merge_columns['source']}",
            {', '.join(source_columns)}
        FROM {config.schemas['pre_transform']}.{source_table}
    """

    transformed_query = f"""
        SELECT
            {merge_columns['transformed']},
            {', '.join(transformed_columns)}
        FROM {config.schemas['post_transform']}.{destination_table}
        {destination_condition}
    """

    return (simple_matches, merge_columns, source_query, transformed_query, module_name)


@case(tags="default")
def case_deputies_2(test_config):
    defaults = {
        "type": "actor_deputy",
        "systemstatus": True,
        "isreplacementattorney": False,
        "istrustcorporation": False,
        "clientstatus": "Active",
        "newsletter": False,
        "digital": False,
        "isorganisation": False,
        "casesmanagedashybrid": False,
        "supervisioncaseowner_id": 10,
        "clientsource": "Casrec",
    }

    config = test_config
    source_columns = [f'"{x}"' for x in defaults.keys()]

    source_query = f"""
        SELECT
            {', '.join(source_columns)}
        FROM {config.schemas['post_transform']}.{destination_table}
        {destination_condition}
    """

    return (defaults, source_query, module_name)


@case(tags="lookups")
# title is commented out because the anon data is wrong so it will never pass
def case_deputies_3(test_config):

    lookup_fields = {
        # "salutation": {"Title": "title_codes_lookup"},
        "correspondencebyemail": {
            "By Email": "Corres_Indicator_lookup"
        },  # lookup needs null value
        # "correspondencebywelsh": {"Welsh": "Welsh_indicator_lookup"} # lookup currently doesn't exist
    }
    merge_columns = {"source": "Email", "transformed": "email"}

    config = test_config

    source_columns = [f'"{y}"' for x in lookup_fields.values() for y in x]
    transformed_columns = [f'"{x}"' for x in lookup_fields.keys()]

    source_query = f"""
        SELECT
            "{merge_columns['source']}",
            {', '.join(source_columns)}
        FROM {config.schemas['pre_transform']}.{source_table}
    """

    transformed_query = f"""
        SELECT
            {merge_columns['transformed']},
            {', '.join(transformed_columns)}
        FROM {config.schemas['post_transform']}.{destination_table}
        {destination_condition}
    """

    return (lookup_fields, merge_columns, source_query, transformed_query, module_name)


@case(tags="calculated")
def case_deputies_4(test_config):

    today = pd.Timestamp.today()

    calculated_fields = {
        "statusdate": today,
        "updateddate": today,
    }
    config = test_config

    source_columns = [f'"{x}"' for x in calculated_fields.keys()]

    source_query = f"""
        SELECT
            {', '.join(source_columns)}
        FROM {config.schemas['post_transform']}.persons
        {destination_condition}
    """

    return (calculated_fields, source_query, module_name)


@case(tags="row_count")
def case_deputies_count(test_config):

    config = test_config
    source_query = f"""
        SELECT
            *
        FROM {config.schemas['pre_transform']}.{source_table}
    """

    transformed_query = f"""
        SELECT
            *
        FROM {config.schemas['post_transform']}.{destination_table}
        {destination_condition}
    """

    return (source_query, transformed_query, module_name)
