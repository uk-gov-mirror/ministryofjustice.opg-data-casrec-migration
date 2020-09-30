import pandas as pd
from sqlalchemy import create_engine


def generate_sirius_object(sirius_table, links, schema, engine):
    # Extract the columns so we can use them to create empty destination table
    sirius_table_columns = sirius_table["to_field"]
    sirius_table_destination = pd.DataFrame(columns=sirius_table_columns)

    # Get list of columns that have mappings to use in our extract query
    tables_rows_for_query = sirius_table.loc[sirius_table["from_table"] != "no_table"]

    # Extract the individual tables (set makes them unique)
    table_set = set()
    for table in tables_rows_for_query["from_table"]:
        table_set.add(table)

    # Extract the column/table pairs for the SELECT bit (set makes them unique)
    col_tbl_pair = tables_rows_for_query[["from_table", "from_column"]].apply(
        lambda row: '"."'.join(row.values.astype(str)), axis=1
    )
    tbl_col_set = set()
    for tbl_col in col_tbl_pair:
        tbl_col_set.add(tbl_col)

    # Create SELECT portion of the statement
    select_cols = ", ".join('"' + item + '"' for item in tbl_col_set)
    sql = f"""
    SELECT {select_cols}
    FROM """

    prev_table = None
    if len(table_set) > 1:
        for table in table_set:
            if prev_table is None:
                sql += f'"{schema}"."{table}"'
            else:
                print(prev_table)
                print(table)
                print(links)
                # Search for the first match in links table
                left_right = links.loc[
                    (links.table_left == prev_table) & (links.table_right == table)
                ]
                print(left_right)
                for i, row in left_right.head(1).iterrows():
                    field_right = row["field_right"]
                    field_left = row["field_left"]
                    table_left = row["table_left"]
                    table_right = row["table_right"]

                sql += f'\nleft join "{schema}"."{table_right}" on "{table_left}"."{field_left}" = "{table_right}"."{field_right}"'
            prev_table = table
    else:
        first_tbl = "".join(table_set)
        sql += f'"{schema}"."{first_tbl}"'

    print(sql)

    sql_results = pd.read_sql_query(sql, engine)

    # Insert into Sirius dataframe
    for i, row in tables_rows_for_query.iterrows():
        sirius_table_destination[row["to_field"]] = sql_results[row["from_column"]]

    return sirius_table_destination


def do_other_stuff(table):
    table["id"] = 9999
    return table


def check_table_exists(table_name, schema_name, engine):
    check_exists_statement = f"""
    SELECT EXISTS (
       SELECT FROM information_schema.tables
       WHERE  table_schema = '{schema_name}'
       AND    table_name   = '{table_name}'
    );
    """

    check_exists_result = engine.execute(check_exists_statement)
    for r in check_exists_result:
        table_exists = r.values()[0]

        return table_exists


def create_table_statement(table_name, schema, columns):
    create_statement = f'CREATE TABLE "{schema}"."{table_name}" ('
    for i, col in enumerate(columns):
        create_statement += f'"{col}" text'
        if i + 1 < len(columns):
            create_statement += ","
    create_statement += "); \n\n\n"

    return create_statement


def create_insert_statement(table_name, schema, columns, df):
    insert_statement = f'INSERT INTO "{schema}"."{table_name}" ('
    for i, col in enumerate(columns):
        insert_statement += f'"{col}"'
        if i + 1 < len(columns):
            insert_statement += ","

    insert_statement += ") \n VALUES \n"

    for i, row in enumerate(df.values.tolist()):
        row = [str(x) for x in row]
        row = [str(x.replace("'", "''").replace("nan", "")) for x in row]
        row = [f"'{str(x)}'" for x in row]
        single_row = ", ".join(row)

        insert_statement += f"({single_row})"

        if i + 1 < len(df):
            insert_statement += ",\n"
        else:
            insert_statement += ";\n\n\n"
    return insert_statement


def get_rows_inserted(table_name, schema_name, engine):
    get_count_statement = f"""
        SELECT COUNT(*) FROM {schema_name}.{table_name};
        """
    get_count_result = engine.execute(get_count_statement)
    for r in get_count_result:
        count = r.values()[0]

        return count


def create_schema(schema, engine):
    schema_exist_statement = f"""
    SELECT
    EXISTS(SELECT
    1
    FROM
    information_schema.schemata
    WHERE
    schema_name = '{schema}');
    """

    schema_exists_result = engine.execute(schema_exist_statement)
    for r in schema_exists_result:
        exists = r.values()[0]

    if not exists:
        print(f"Creating schema {schema}...")
        create_schema_sql = f"CREATE SCHEMA {schema} AUTHORIZATION casrec;"
        engine.execute(create_schema_sql)
        print(f"Schema {schema} created\n\n")
    else:
        print(f"Schema {schema} already exists\n\n")


def load_table(df, table_name, schema, engine):
    df_renamed = df.rename(columns={"Unnamed: 0": "Record"})

    columns = [x for x in df_renamed.columns.values]

    if check_table_exists(table_name, schema, engine):
        print(f"Truncating table {schema}.{table_name}")
        truncate_statement = f'TRUNCATE TABLE "{schema}"."{table_name}"'
        engine.execute(truncate_statement)
    else:
        print(f"Table {schema}.{table_name} doesn't exist. Creating table...")
        engine.execute(create_table_statement(table_name, schema, columns))
        print(f"Table {schema}.{table_name} created")

    print(f'Inserting records into "{schema}"."{table_name}"')
    engine.execute(create_insert_statement(table_name, schema, columns, df_renamed))
    print(
        f'Rows inserted into "{schema}"."{table_name}": {get_rows_inserted(table_name, schema, engine)}\n\n'
    )


engine_string = "postgresql+psycopg2://casrec:casrec@localhost:6666/casrecmigration"  # pragma: allowlist secret
sql_engine = create_engine(engine_string)

customer_data_file = "test_load.xlsx"

schema_from = "etl1"
schema_to = "etl2"

table_links = pd.read_excel(customer_data_file, sheet_name="links")

remarks = pd.read_excel(customer_data_file, sheet_name="remarks")
person = pd.read_excel(customer_data_file, sheet_name="person")

remarks_df = generate_sirius_object(remarks, table_links, schema_from, sql_engine)
person_df = generate_sirius_object(person, table_links, schema_from, sql_engine)

remarks_final = do_other_stuff(remarks_df)
person_final = do_other_stuff(person_df)

print(remarks_final)
print(person_final)

print(f"Creating schema {schema_to}")
create_schema(schema_to, sql_engine)

load_table(remarks_final, "remarks", schema_to, sql_engine)
load_table(person_final, "person", schema_to, sql_engine)
