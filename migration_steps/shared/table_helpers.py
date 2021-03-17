import json
import os
from collections import OrderedDict


def get_current_directory():
    dirname = os.path.dirname(__file__)
    return dirname


def get_table_file(file_name="tables"):
    dirname = get_current_directory()
    file_path = os.path.join(dirname, f"{file_name}.json")

    with open(file_path) as tables_json:
        tables_dict = json.load(tables_json, object_pairs_hook=OrderedDict)

    return tables_dict


def get_table_list(table_dict, type=None):
    if type:

        return [k for k, v in table_dict.items() if v["table_type"] == type]
    else:
        return list(table_dict.keys())


def get_fk_cols_single_table(table):
    table_as_dict = json.loads(json.dumps(table))

    return [v for y in table_as_dict["fks"] for k, v in y.items() if k == "column"]


def get_sequences_list(table_dict, type="pk"):
    sequence_list = []
    for table, details in table_dict.items():
        for seq in details["sequences"]:
            if seq["type"] == type:
                table_seq = {
                    "sequence_name": seq["name"],
                    "table": table,
                    "column": seq["column"],
                }
                sequence_list.append(table_seq)
    return sequence_list


def get_uid_sequences_list(table_dict):
    sequence_list = []
    for table, details in table_dict.items():
        for seq in details["sequences"]:
            if seq["type"] == "uid":
                if any(seq["name"] in x["sequence_name"] for x in sequence_list):
                    additional_fields = {"table": table, "column": seq["column"]}

                    pos = [
                        i
                        for i, s in enumerate(sequence_list)
                        if seq["name"] in s["sequence_name"]
                    ][0]
                    sequence_list[pos]["fields"].append(additional_fields)
                else:
                    table_seq = {
                        "sequence_name": seq["name"],
                        "fields": [{"table": table, "column": seq["column"]}],
                    }
                    sequence_list.append(table_seq)
    return sequence_list


def get_pk(engine, schema, table):
    get_pk_statement = f"""
        SELECT col.Column_Name from
        INFORMATION_SCHEMA.TABLE_CONSTRAINTS tab,
        INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE col
        WHERE
        col.Constraint_Name = tab.Constraint_Name
        AND col.Table_Name = tab.Table_Name
        AND Constraint_Type = 'PRIMARY KEY'
        AND tab.table_schema = '{schema}'
        AND col.Table_Name = '{table}'
        """
    response = engine.execute(get_pk_statement)
    for r in response:
        primary_key = r.values()
        return primary_key
