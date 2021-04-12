import datetime
import json
import os
import sys
from pathlib import Path
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../shared")
from helpers import get_timeline_dict, get_config

log = logging.getLogger("root")

DEFAULT_USER_ID = 1
TIMELINE_TABLE_COLS = {
    "id": "int",
    "user_id": "int",
    "timestamp": "timestamp(0)",
    "eventtype": "varchar(255)",
    "event": "json",
    "c_casrec_row_id": "int",
    "c_sirius_table": "text",
    "c_sirius_table_id": "int",
}


def prep_timeline_data(timeline_dict, db_config):

    cols = ", ".join(
        f'"{col}" as "{alias}"' for col, alias in timeline_dict["timeline_cols"].items()
    )

    timeline_data_query = f"""
        SELECT {cols}, casrec_row_id
        FROM {db_config['source_schema']}.{timeline_dict['casrec_table']};
    """

    timeline_data_df = pd.read_sql_query(
        sql=timeline_data_query, con=db_config["db_connection_string"]
    )

    important_cols = [v for k, v in timeline_dict["timeline_cols"].items()]

    timeline_data_df = timeline_data_df.replace("", np.nan)
    timeline_data_df = timeline_data_df.dropna(subset=important_cols, thresh=1)
    timeline_data_df = timeline_data_df.replace(np.nan, "")

    base_data_query = f"""
        SELECT id, cast(casrec_row_id as int)
        FROM {db_config['target_schema']}.{timeline_dict['sirius_table']}
    """

    base_data_df = pd.read_sql_query(
        sql=base_data_query, con=db_config["db_connection_string"]
    )

    timeline_data_with_id = timeline_data_df.merge(
        base_data_df, how="left", left_on="casrec_row_id", right_on="casrec_row_id"
    )

    timeline_data_with_id = timeline_data_with_id.rename(
        columns={"id": "sirius_table_id"}
    )

    timeline_data_with_id["sirius_table"] = timeline_dict["sirius_table"]
    timeline_data_with_id["casrec_table"] = timeline_dict["casrec_table"]
    timeline_data_with_id["entity"] = timeline_dict["entity"]

    return timeline_data_with_id


def format_event(df):
    standard_cols = [
        "sirius_table",
        "casrec_table",
        "entity",
        "casrec_row_id",
        "sirius_table_id",
    ]

    cols = df.columns.tolist()
    event_columns = [x for x in cols if x not in standard_cols]

    event_dict = df[[x for x in event_columns]].to_dict("records")

    # this is a hack, format needs working out
    eventtype_list = [str(list(set(df[x].values))[0]) for x in standard_cols]
    eventtype = "_".join(eventtype_list)

    new_df = df[[x for x in standard_cols]].copy()
    new_df["eventtype"] = eventtype
    new_df["event"] = event_dict
    new_df["event"] = new_df["event"].apply(
        lambda x: {"class": eventtype, "payload": x}
    )
    new_df["event"] = new_df["event"].apply(lambda x: json.dumps(x))

    return new_df


def format_other_cols(df):
    cols_required = [x for x in TIMELINE_TABLE_COLS]

    df.insert(0, "id", range(1, 1 + len(df)))
    df["user_id"] = DEFAULT_USER_ID
    df["timestamp"] = datetime.datetime.now()
    df = df.rename(
        columns={
            "casrec_row_id": "c_casrec_row_id",
            "sirius_table": "c_sirius_table",
            "sirius_table_id": "c_sirius_table_id",
        }
    )

    formatted_df = df[[x for x in cols_required]]

    return formatted_df


def create_table(timeline_table_name, db_config, target_db):

    cols_to_create = [f"{k} {v}" for k, v in TIMELINE_TABLE_COLS.items()]

    create_timeline_table_statement = f"""
        CREATE TABLE {db_config['target_schema']}.{timeline_table_name} (
            {', '.join(cols_to_create)}
               );
    """

    try:
        with target_db.begin() as conn:
            conn.execute(create_timeline_table_statement)

    except Exception as e:
        print("TERRIBLE ERRORROROROR creating the table - probs already exists")
        print(f"e: {e}")


def create_insert_statement(db_config, timeline_table_name, df):
    cols = [x for x in TIMELINE_TABLE_COLS]

    insert_statement = f"""
        INSERT INTO {db_config['target_schema']}.{timeline_table_name} ({', '.join(cols)})
        VALUES
    """

    sample = df.sample(2)

    for i, row in enumerate(sample.values.tolist()):
        row = [str(x) for x in row]
        row = [f"'{str(x)}'" if str(x) != "" else "NULL" for x in row]
        single_row = ", ".join(row)

        insert_statement += f"({single_row})"

        if i + 1 < len(sample):
            insert_statement += ",\n"
        else:
            insert_statement += ";\n\n\n"

    return insert_statement


def insert_timeline(db_config, timeline_file_name):
    config = get_config(env=os.environ.get("ENVIRONMENT"))

    allowed_entities = [k for k, v in config.ENABLED_ENTITIES.items() if v is True]

    target_db_engine = create_engine(db_config["db_connection_string"])

    timeline_dict = get_timeline_dict(file_name=timeline_file_name)

    if not timeline_dict["entity"] in allowed_entities:
        log.info(
            f"{timeline_file_name} is party of entity '{timeline_dict['entity']}'  which is not enabled, moving on"
        )
        return False

    timeline_table_name = (
        f"timeline_event_{timeline_dict['entity']}_{timeline_dict['sirius_table']}"
    )

    create_table(
        timeline_table_name=timeline_table_name,
        db_config=db_config,
        target_db=target_db_engine,
    )

    timeline_data_df = prep_timeline_data(
        timeline_dict=timeline_dict, db_config=db_config
    )

    timeline_data_df = format_event(df=timeline_data_df)
    timeline_data_df = format_other_cols(df=timeline_data_df)

    insert_statement = create_insert_statement(
        db_config=db_config,
        timeline_table_name=timeline_table_name,
        df=timeline_data_df,
    )

    try:

        with target_db_engine.begin() as conn:

            inserted = conn.execute(insert_statement)
            log.debug(f"inserted {inserted.rowcount} rows into {timeline_table_name}")

    except Exception as e:
        log.error("TERRIBLE ERRORROROROR inserting into the table")
        print(f"e: {e}")
