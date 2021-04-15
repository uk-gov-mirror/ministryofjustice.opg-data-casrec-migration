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
from helpers import get_additional_data_dict, get_config

log = logging.getLogger("root")

DEFAULT_USER_ID = 2
additional_data_TABLE_COLS = {
    "id": "int",
    "entity": "varchar(255)",
    "details": "json",
    "sirius_table": "text",
    "sirius_pk_column": "text",
    "sirius_pk": "int",
    "c_casrec_row_id": "int",
    # "transformation_schema_id": "int",
}


def prep_additional_data_data(additional_data_dict, db_config, chunk_details=None):

    cols = ", ".join(
        f'"{col}" as "{alias}"'
        for col, alias in additional_data_dict["timeline_cols"].items()
    )

    additional_data_data_query = f"""
        SELECT {cols}, casrec_row_id
        FROM {db_config['source_schema']}.{additional_data_dict['casrec_table']}
    """

    if chunk_details:
        additional_data_data_query += f"""
        ORDER BY casrec_row_id LIMIT {chunk_details["chunk_size"]} OFFSET {chunk_details["offset"]};
        """

    additional_data_data_df = pd.read_sql_query(
        sql=additional_data_data_query, con=db_config["db_connection_string"]
    )

    important_cols = [v for k, v in additional_data_dict["timeline_cols"].items()]

    additional_data_data_df = additional_data_data_df.replace("", np.nan)
    additional_data_data_df = additional_data_data_df.dropna(
        subset=important_cols, thresh=1
    )
    additional_data_data_df = additional_data_data_df.replace(np.nan, "")

    base_data_query = f"""
        SELECT id, cast(casrec_row_id as int)
        FROM {db_config['target_schema']}.{additional_data_dict['sirius_table']}
    """

    base_data_df = pd.read_sql_query(
        sql=base_data_query, con=db_config["db_connection_string"]
    )

    additional_data_data_with_id = additional_data_data_df.merge(
        base_data_df, how="left", left_on="casrec_row_id", right_on="casrec_row_id"
    )

    additional_data_data_with_id = additional_data_data_with_id.rename(
        columns={"id": "sirius_table_id"}
    )

    additional_data_data_with_id["sirius_table"] = additional_data_dict["sirius_table"]
    additional_data_data_with_id["casrec_table"] = additional_data_dict["casrec_table"]
    additional_data_data_with_id["entity"] = additional_data_dict["entity"]

    return additional_data_data_with_id


def format_event(df):
    standard_cols = [
        "sirius_table",
        "casrec_table",
        "entity",
        "casrec_row_id",
        "sirius_table_id",
    ]

    cols = df.columns.tolist()
    # event_columns = [x for x in cols if x not in standard_cols]
    event_columns = [x for x in cols if x not in ["casrec_table", "casrec_row_id"]]

    event_dict = df[[x for x in event_columns]].to_dict("records")

    # this is a hack, format needs working out
    # eventtype_list = [str(list(set(df[x].values))[0]) for x in standard_cols]
    # eventtype = "_".join(eventtype_list)

    new_df = df[[x for x in standard_cols]].copy()
    # new_df["eventtype"] = eventtype
    new_df["details"] = event_dict
    # new_df["details"] = new_df["event"].apply(
    #     lambda x: {"class": eventtype, "payload": x}
    # )
    new_df["details"] = new_df["details"].apply(lambda x: json.dumps(x))

    return new_df


def format_other_cols(df):
    cols_required = [x for x in additional_data_TABLE_COLS]

    df.insert(0, "id", range(1, 1 + len(df)))
    df["user_id"] = DEFAULT_USER_ID
    df["timestamp"] = datetime.datetime.now()
    df = df.rename(
        columns={
            "casrec_row_id": "c_casrec_row_id",
            "sirius_table": "sirius_table",
            # "sirius_column": "sirius_pk_column",
            "sirius_table_id": "sirius_pk",
        }
    )
    df["transformation_schema_id"] = df["sirius_pk"]
    df["sirius_pk_column"] = "id"

    formatted_df = df[[x for x in cols_required]]
    print(formatted_df)

    return formatted_df


def create_table(additional_data_table_name, db_config, target_db):

    cols_to_create = [f"{k} {v}" for k, v in additional_data_TABLE_COLS.items()]

    create_additional_data_table_statement = f"""
        CREATE TABLE {db_config['target_schema']}.{additional_data_table_name} (
            {', '.join(cols_to_create)}
               );
    """

    try:
        with target_db.begin() as conn:
            conn.execute(create_additional_data_table_statement)

    except Exception as e:
        log.error(
            f"table {additional_data_table_name} could not be created (probably already exists)"
        )
        print(f"e: {e}")


def create_insert_statement(db_config, additional_data_table_name, df):
    cols = [x for x in additional_data_TABLE_COLS]

    insert_statement = f"""
        INSERT INTO {db_config['target_schema']}.{additional_data_table_name} ({', '.join(cols)})
        VALUES
    """

    # df = df.sample(2)

    for i, row in enumerate(df.values.tolist()):
        row = [str(x) for x in row]
        row = [
            str(
                x.replace("'", "''")
                .replace("NaT", "")
                .replace("nan", "")
                .replace("<NA>", "")
                .replace("&", "and")
                .replace(";", "-")
                .replace("%", "percent")
            )
            for x in row
        ]
        row = [f"'{str(x)}'" if str(x) != "" else "NULL" for x in row]
        single_row = ", ".join(row)

        insert_statement += f"({single_row})"

        if i + 1 < len(df):
            insert_statement += ",\n"
        else:
            insert_statement += ";\n\n\n"

    return insert_statement


def insert_additional_data_records(db_config, additional_data_file_name):

    config = get_config(env=os.environ.get("ENVIRONMENT"))
    chunk_size = config.DEFAULT_CHUNK_SIZE
    offset = 0
    chunk_no = 1

    allowed_entities = [k for k, v in config.ENABLED_ENTITIES.items() if v is True]

    target_db_engine = create_engine(db_config["db_connection_string"])

    additional_data_dict = get_additional_data_dict(file_name=additional_data_file_name)

    if not additional_data_dict["entity"] in allowed_entities:
        log.info(
            f"{additional_data_file_name} is party of entity '{additional_data_dict['entity']}'  which is not enabled, moving on"
        )
        return False

    additional_data_table_name = f"additional_data_{additional_data_dict['entity']}_{additional_data_dict['sirius_table']}"

    create_table(
        additional_data_table_name=additional_data_table_name,
        db_config=db_config,
        target_db=target_db_engine,
    )

    while True:

        try:

            additional_data_data_df = prep_additional_data_data(
                additional_data_dict=additional_data_dict,
                db_config=db_config,
                chunk_details={"chunk_size": chunk_size, "offset": offset},
            )

            additional_data_data_df = format_event(df=additional_data_data_df)
            additional_data_data_df = format_other_cols(df=additional_data_data_df)

            insert_statement = create_insert_statement(
                db_config=db_config,
                additional_data_table_name=additional_data_table_name,
                df=additional_data_data_df,
            )

            try:

                with target_db_engine.begin() as conn:
                    log.debug(f"inserting chunk no {chunk_no}")
                    inserted = conn.execute(insert_statement)
                    log.debug(
                        f"inserted {inserted.rowcount} rows into {additional_data_table_name}"
                    )

            except Exception as e:
                log.error("TERRIBLE ERRORROROROR inserting into the table")
                print(f"e: {e}")

            offset += chunk_size
            chunk_no += 1

        except Exception:

            break
