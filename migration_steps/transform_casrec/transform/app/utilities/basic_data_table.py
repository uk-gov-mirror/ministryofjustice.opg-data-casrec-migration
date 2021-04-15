import pandas as pd
from helpers import get_mapping_dict
from transform_data import transform
from utilities.generate_source_query import generate_select_string_from_mapping
import logging

log = logging.getLogger("root")


def get_source_table(mapping_dict):
    source_table_list = [
        v["casrec_table"].lower()
        for k, v in mapping_dict.items()
        if v["casrec_table"] != ""
    ]
    no_dupes = list(set(source_table_list))
    if len(no_dupes) == 1:
        return list(set(source_table_list))[0]
    else:
        log.error("Multiple source tables")
        return ""


def get_basic_data_table(
    mapping_file_name, table_definition, db_config, chunk_details=None
):
    log.debug(f"Getting basic data using {mapping_file_name}")

    mapping_dict = get_mapping_dict(
        file_name=mapping_file_name, stage_name="transform_casrec"
    )

    source_table = get_source_table(mapping_dict=mapping_dict)

    sirius_details = get_mapping_dict(
        file_name=mapping_file_name,
        stage_name="sirius_details",
        only_complete_fields=False,
    )

    source_data_query = generate_select_string_from_mapping(
        mapping=mapping_dict,
        source_table_name=source_table,
        additional_columns=table_definition["source_table_additional_columns"],
        db_schema=db_config["source_schema"],
        chunk_details=chunk_details,
    )

    source_data_df = pd.read_sql_query(
        sql=source_data_query, con=db_config["db_connection_string"]
    )

    result_df = transform.perform_transformations(
        mapping_definitions=mapping_dict,
        table_definition=table_definition,
        source_data_df=source_data_df,
        db_conn_string=db_config["db_connection_string"],
        db_schema=db_config["target_schema"],
        sirius_details=sirius_details,
    )

    result_df["casrec_mapping_file_name"] = mapping_file_name

    log.debug(f"Basic data for {mapping_file_name} has {len(result_df)} rows")

    return sirius_details, result_df
