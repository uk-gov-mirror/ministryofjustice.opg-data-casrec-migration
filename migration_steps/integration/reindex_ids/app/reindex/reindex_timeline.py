from sqlalchemy import create_engine
import logging
import pandas as pd

log = logging.getLogger("root")


def get_timeline_tables(db_config):
    target_db_engine = create_engine(db_config["db_connection_string"])

    table_names_query = f"""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = '{db_config['source_schema']}';
        """

    try:

        with target_db_engine.begin() as conn:
            tables_return = conn.execute(table_names_query).fetchall()

            return [x[0] for x in tables_return if "timeline_event_" in x[0]]

    except Exception as e:
        log.error("TERRIBLE ERRORROROROR getting table names")
        print(f"e: {e}")


def get_source_table_details(db_config, table):
    target_db_engine = create_engine(db_config["db_connection_string"])
    query = f"""
        SELECT c_sirius_table
        FROM {db_config['source_schema']}.{table}
        LIMIT 1
    """
    try:

        with target_db_engine.begin() as conn:
            table_details = conn.execute(query).fetchall()
            print(f"table_details: {table_details}")

        return table_details[0][0]
    except Exception as e:
        log.error("TERRIBLE ERRORROROROR getting table names")
        print(f"e: {e}")


def update_timeline_id(db_config, table):
    target_db_engine = create_engine(db_config["db_connection_string"])
    # schema = db_config['target_schema']
    schema = "transform"
    source_table = get_source_table_details(db_config=db_config, table=table)

    update_statement = f"""
        UPDATE {schema}.{table}
        SET c_sirius_table_id = id
        FROM {schema}.{source_table}
        WHERE {table}.transformation_schema_id = {source_table}.transformation_schema_id;

    """
    try:

        with target_db_engine.begin() as conn:
            udpated = conn.execute(update_statement).fetchall()

        log.info(f"{udpated.rowcount} rows updated")
    except Exception as e:
        log.error("TERRIBLE ERRORROROROR getting table names")
        print(f"e: {e}")


def update_timeline_json(db_config, table):
    # target_db_engine = create_engine(db_config["db_connection_string"])
    # schema = db_config['target_schema']
    schema = "transform"

    timeline_table_query = f"""
        SELECT event, c_sirius_table_id FROM {schema}.{table};
    """
    timeline_table_df = pd.read_sql_query(
        sql=timeline_table_query, con=db_config["db_connection_string"]
    )

    def add_key(row, new_thing):
        for key, value in row["event"].items():
            if key == "payload":
                value["sirius_table_id"] = new_thing

        return row

    timeline_table_df["event"] = timeline_table_df.apply(
        lambda x: add_key(row=x, new_thing=x["c_sirius_table_id"]), axis=1
    )
    print(timeline_table_df.sample(2).to_markdown())
