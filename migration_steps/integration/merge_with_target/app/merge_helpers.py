import logging

import psycopg2

log = logging.getLogger("root")


def generate_select_query(schema, table, columns):
    query = f"SELECT {', '.join(columns)} from {schema}.{table};"

    return query


def generate_max_id_query(schema, table, id="id"):
    query = f"SELECT max({id}) from {schema}.{table};"

    return query


def get_max_id_from_sirius(db_config, table, id="id"):
    connection_string = db_config["sirius_db_connection_string"]
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    query = generate_max_id_query(schema=db_config["sirius_schema"], table=table, id=id)

    try:
        cursor.execute(query)
        max_id = cursor.fetchall()
        return max_id[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


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

    max_id = get_max_id_from_sirius(db_config=db_config, table=table)
    first_id = int(max_id) + 1

    new_df = df[df["method"] == "INSERT"]

    new_df = new_df.rename(columns={"id": "transformation_id"})

    new_df.insert(0, "id", range(first_id, first_id + len(new_df)))

    log.debug(
        f"Found {len(new_df.index)} new rows to add to the {table} table "
        f"with ids between {new_df['id'].iloc[0]} and "
        f"{new_df['id'].iloc[-1]}"
    )

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
