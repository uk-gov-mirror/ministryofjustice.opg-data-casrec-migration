def clear_tables(db_engine, db_config):
    schema = db_config["target_schema"]

    # reset uids in persons and cases
    persons_statement = f"UPDATE {schema}.persons SET uid = NULL;"
    cases_statement = f"UPDATE {schema}.cases SET uid = NULL;"

    conn = db_engine.connect()
    conn.execute(persons_statement)
    conn.execute(cases_statement)
    conn.close()
