import os
import pandas as pd


anon_data_dir = '../anon_data'
target_dir = '../sql'


for file in os.listdir(anon_data_dir):

    file_name = file.split('.')[0]
    sql_out = open(os.path.join(target_dir, f'{file_name}.sql'), "w")


    df = pd.read_csv(os.path.join(anon_data_dir, file))
    df_renamed = df.rename(columns ={'Unnamed: 0': "Record"})

    columns = [x for x in df_renamed.columns.values]

    create_statement = f"CREATE TABLE \"{file_name}\" ("
    for i, col in enumerate(columns):
        create_statement += f"\"{col}\" text"
        if i+1 < len(columns):
            create_statement += ","

    create_statement += "); \n\n\n"
    sql_out.write(create_statement)

    insert_statement = f"INSERT INTO \"{file_name}\" ("
    for i, col in enumerate(columns):
        insert_statement += f"\"{col}\""
        if i + 1 < len(columns):
            insert_statement += ","

    insert_statement += ") \n VALUES \n"
    for i, row in enumerate(df.values.tolist()):
        row = [str(x) for x in row]
        row = [str(x.replace("'", "''").replace("nan", "")) for x in row]
        row = [f"\'{str(x)}\'" for x in row]
        single_row = ', '.join(row)

        insert_statement += f"({single_row})"

        if i + 1 < len(df):
            insert_statement += ",\n"
        else:
            insert_statement += ";\n\n\n"

    sql_out.write(insert_statement)


sql_out.close()

