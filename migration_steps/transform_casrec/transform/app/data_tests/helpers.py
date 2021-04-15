import pandas as pd

from config import get_config
import numpy as np

config = get_config()

sample_percentage = config.SAMPLE_PERCENTAGE


def get_data_from_query(
    query, config, sort_col=None, sample=False, sample_percentage=sample_percentage
):

    df = pd.read_sql_query(query, config.get_db_connection_string(db="migration"))

    df.replace([None, ""], "", inplace=True)

    if sample:
        df = df.sample(frac=sample_percentage / 100, replace=False, random_state=1)

    if sort_col:
        return df.sort_values(by=[sort_col])
    else:
        return df


def get_merge_col_data_as_list(df, column_name):

    col = df[column_name].to_list()
    return col


def merge_source_and_transformed_df(source_df, transformed_df, merge_columns):
    return source_df.merge(
        transformed_df,
        how="inner",
        left_on=merge_columns["source"],
        right_on=merge_columns["transformed"],
    )
