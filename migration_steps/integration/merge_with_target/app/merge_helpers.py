import logging

import psycopg2

# from utilities.generate_luhn_checksum import append_checksum
from utilities.generate_luhn_checksum import append_checksum

log = logging.getLogger("root")


def generate_select_query(schema, table, columns=None, where_clause=None):
    if columns:
        query = f"SELECT {', '.join(columns)} from {schema}.{table}"
    else:
        query = f"SELECT * from {schema}.{table}"

    if where_clause:
        where = ""
        for i, (item, value) in enumerate(where_clause.items()):
            if i == 0:
                where += " WHERE "
            else:
                where += " AND "

            where += f"{item} = '{value}'"

        query += where

    query += ";"

    return query


def generate_max_id_query(schema, table, id="id"):
    query = f"SELECT max({id}) from {schema}.{table};"

    return query


def get_max_id_from_existing_table(db_connection_string, db_schema, table, id="id"):
    connection_string = db_connection_string
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    query = generate_max_id_query(schema=db_schema, table=table, id=id)

    try:
        cursor.execute(query)
        max_id = cursor.fetchall()[0][0]
        if max_id:
            log.debug(f"Max '{id}' in table '{db_schema}.{table}': {max_id}")
            return max_id
        else:
            log.debug(
                f"No data for '{id}' in table '{db_schema}.{table}', setting max_id to 0"
            )
            return 0

        cursor.close()
    except psycopg2.DatabaseError:
        log.debug(
            f"No data for '{id}' in table '{db_schema}.{table}', setting max_id to 0"
        )
        return 0
    except (Exception) as error:
        log.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1


def calculate_new_uid(db_config, df, table, column_name):

    sirius_max_uid = get_max_id_from_existing_table(
        db_connection_string=db_config["sirius_db_connection_string"],
        db_schema=db_config["sirius_schema"],
        table=table,
        id=column_name,
    )

    target_max_uid = get_max_id_from_existing_table(
        db_connection_string=db_config["db_connection_string"],
        db_schema=db_config["target_schema"],
        table=table,
        id=column_name,
    )

    try:
        sirius_max_uid_without_checksum = int(str(sirius_max_uid)[:-1])
    except ValueError:
        sirius_max_uid_without_checksum = 0
    try:
        target_max_uid_without_checksum = int(str(target_max_uid)[:-1])
    except ValueError:
        target_max_uid_without_checksum = 0

    next_uid_without_checksum = (
        sirius_max_uid_without_checksum + target_max_uid_without_checksum + 1
    )
    log.debug(
        f"Starting with uid {next_uid_without_checksum} (without final checksum digit)"
    )

    df.insert(
        0,
        "uid_no_checksum",
        range(next_uid_without_checksum, next_uid_without_checksum + len(df)),
    )
    df[column_name] = df["uid_no_checksum"].apply(lambda x: append_checksum(x))
    df = df.drop(columns="uid_no_checksum")

    return df


def merge_source_data_with_existing_data(source_data, existing_data, match_columns):

    result_df = source_data.merge(
        existing_data, how="left", left_on=match_columns, right_on=match_columns
    )

    result_df["sirius_id"] = result_df["id_y"]
    result_df["sirius_id"] = result_df["sirius_id"].fillna(0)
    result_df["sirius_id"] = result_df["sirius_id"].astype(int)
    result_df["method"] = result_df.apply(
        lambda x: "INSERT" if x["sirius_id"] == 0 else "UPDATE", axis=1
    )

    result_df = result_df.drop(columns="id_y")
    result_df = result_df.rename(columns={"id_x": "id"})

    return result_df


def reindex_new_data(db_config, df, table):

    sirius_max_id = get_max_id_from_existing_table(
        db_connection_string=db_config["sirius_db_connection_string"],
        db_schema=db_config["sirius_schema"],
        table=table,
    )
    target_max_id = get_max_id_from_existing_table(
        db_connection_string=db_config["db_connection_string"],
        db_schema=db_config["target_schema"],
        table=table,
    )

    first_id = int(sirius_max_id) + int(target_max_id) + 1
    log.debug(f"Starting with id {first_id}")

    try:
        no_of_rows = len(df.index)

        # new_df = df[df["method"] == "INSERT"]

        new_df = df.rename(columns={"id": "transformation_id"})

        new_df.insert(0, "id", range(first_id, first_id + len(new_df)))

    except IndexError:
        no_of_rows = 0
        new_df = df

    log.debug(f"Found {no_of_rows} new rows to add to the {table} table ")

    return new_df


def reindex_existing_data(df, table):
    update_df = df[df["method"] == "UPDATE"]
    update_df = update_df.rename(columns={"id": "transformation_id"})
    update_df["id"] = update_df["sirius_id"]
    log.debug(
        f"Found {len(update_df.index)} existing rows to update in the {table} " f"table"
    )

    return update_df


def update_foreign_keys(df, parent_df, fk_details):

    parent_df[f"transformation_{fk_details['parent_col']}"] = parent_df[
        f"transformation_{fk_details['parent_col']}"
    ].astype(int)

    result_df = df.merge(
        parent_df,
        how="left",
        left_on=fk_details["fk_col"],
        right_on=f"transformation_{fk_details['parent_col']}",
    )

    result_df = result_df.rename(
        columns={
            fk_details["fk_col"]: f"transformation_{fk_details['fk_col']}",
            "id_y": fk_details["fk_col"],
            "id_x": "id",
            "transformation_id_x": "transformation_id",
        }
    )

    result_df = result_df.dropna(subset=[fk_details["fk_col"]])

    result_df = result_df.reset_index()
    result_df = result_df.drop(
        columns=[f"transformation_{fk_details['parent_col']}_y", "index"]
    )

    result_df[fk_details["fk_col"]] = result_df[fk_details["fk_col"]].astype(int)
    return result_df
