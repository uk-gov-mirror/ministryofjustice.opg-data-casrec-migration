# Adding a new entity



[TOC]





## Introduction

### Definitions

* An *entity* is a conceptual chunk of Sirius data
* One *entity* can comprise of many *tables*
* A *table* can be of type:
  * data table
  * fk table
  * join table

### Example tables

For this walk through we will be using 3 example tables in the entity `pirates`:

* captains - **data table** *contains personal details of pirate captains*
* crew - **fk table** *contains details of crew members, multiple crew members are linked to one captain by a foreign key*
* captain_ships - **join table** *table of ids linking captains to ships*



## Step 1 - Transform



```bash
Run independently:
	migration_steps/transform_casrec/app/app.py

options:
  --clear=True/False              clear existing data from schema before running
  --entity_list=pirates		run only elected entities, comma separated eg `pirates,booty,shipwrecks`
  --include_tests=True/False	run the data tests after the transform
  -v -vv -vvv                     more v's == more detailed logging
```

### Adding to the transform step

##### data table

1. In `app/entities` add a folder called **pirates**

2. Add an `init.py` to the `pirates` folder containing the following:

   ```python
   import logging
   from entities.pirates.captains import insert_captains
   from helpers import log_title

   log = logging.getLogger("root")

   def runner(config, etl2_db):
       """
       | Name      | Running Order | Requires |
       | --------- | ------------- | -------- |
       | captains  | 1             |          |
       |           |               |          |
       |           |               |          |

       """

       log.info(log_title(message="pirates"))

       log.debug("insert_captains")
       insert_captains(config, etl2_db)

   if __name__ == "__main__":
       runner()
   ```



3. Add a `captains.py` file containing:

   ```python
   from utilities.basic_data_table import get_basic_data_table

   definition = {
       "source_table_name": "Pirate Captain Details",
       "source_table_additional_columns": [],
       "destination_table_name": "captains",
   }

   mapping_file_name = "pirate_captains_mapping"

   def insert_captains(config, etl2_db):
       sirius_details, captains_df = get_basic_data_table(
           config=config, mapping_file_name=mapping_file_name, table_definition=definition
       )

       etl2_db.insert_data(
           table_name=definition["destination_table_name"],
           df=captains_df,
           sirius_details=sirius_details,
       )

   ```

4. Edit `migration_steps/transform_casrec/app/app.py` and add little if to the `main` method:

   ```python
       if len(allowed_entities) == 0 or "pirates" in allowed_entities:
           pirates.runner(config, etl2_db)
   ```


##### fk table

1. Add a crew.py file to the `pirates` folder containing:

   ```python
   from utilities.basic_data_table import get_basic_data_table

   definition = {
       "source_table_name": "Pirate Crew Details",
       # if you need extra columns to join on that are not in the json def, add them to this list
       # they will appear in the df in the format 'c_<column_name>'
       "source_table_additional_columns": ['pirate_number'],
       "destination_table_name": "crew",
   }

   mapping_file_name = "pirate_crew_mapping"

   def insert_crew(config, etl2_db):
       sirius_details, crew_df = get_basic_data_table(
           config=config, mapping_file_name=mapping_file_name, table_definition=definition
       )

       captains_query = (
           f'select "id", "pirate_number" from etl2.pirates '
           f"where \"type\" = 'swarthy';"
       )
       captains_df = pd.read_sql_query(captains_query, config.connection_string)

       #  Depending on your data you may have to do some tweaking in here before you join


       # this 'merge' is the equivalent of:
       # SELECT crew.* from crew left outer join captains on crew.c_pirate_number = captains.pirate_number
       crew_joined_df = crew_df.merge(
           captains_df, how="left", left_on="c_pirate_number", right_on="pirate_number"
       )

       # when you merge dfs and have 2 cols with the same name they are renamed <col>_x and <col>_y
       # 'id_y' here is the 'id' col of the join on table, in this case 'captains.id'
       # here we are renaming it in the crew table to 'captain_id'
       crew_joined_df["captain_id"] = addresses_joined_df["id_y"]

       # then drop the unnecessary 'id_y' col
       crew_joined_df = crew_joined_df.drop(columns=["id_y"])

       # and rename the original crew.id back to id
       crew_joined_df = crew_joined_df.rename(columns={"id_x": "id"})

       etl2_db.insert_data(
           table_name=definition["destination_table_name"],
           df=crew_joined_df,
           sirius_details=sirius_details,
       )


   ```

2. Amend the `init.py` and add the `insert_crew` method

   ```python
       log.debug("insert_crew")
       insert_crew(config, etl2_db)
   ```



3. Update the docstring at the start of the `runner` method - you will be grateful later!

   ```python
   def runner(config, etl2_db):
       """
       | Name      | Running Order | Requires |
       | --------- | ------------- | -------- |
       | captains  | 1             |          |
       | crew      | 2             | captains |
       |           |               |          |

       """
   ```

##### join table

Not required in this step

### Adding to the data tests

tbc

### Additional transformations

tbc

## Step 2 - Integration

### Merge with target

##### data table

1. In `app/entities` add a folder called **pirates**

2. Add an `init.py` to the `pirates` folder containing the following:

   ```python
   import logging

   from entities.pirates import captains, crew

   log = logging.getLogger("root")

   entity_name = "Pirates"


   def merge_source_data(db_config, target_db):
       log.info(f"Entity: {entity_name}")
       log.info(" - Captains")
       captains.merge_source_into_target(db_config, target_db)

       log.info(" - Crew")
       crew.merge_source_into_target(db_config, target_db)
   ```



3. Add a `captains.py` file containing:

   ```python
   import logging
   import os

   import config2
   import pandas as pd
   from helpers import get_mapping_dict

   from merge_helpers import (
       generate_select_query,
       merge_source_data_with_existing_data,
       reindex_existing_data,
       reindex_new_data,
       calculate_new_uid,
   )


   log = logging.getLogger("root")

   environment = os.environ.get("ENVIRONMENT")
   config = config2.get_config(env=environment)

   row_limit = config.row_limit
   table = "captains"
   match_columns = ["pirate_number", "nickname", "beard_colour"]

   mapping_file_name = "pirate_captains_mapping"
   sirius_details = get_mapping_dict(
       file_name=mapping_file_name,
       stage_name="sirius_details",
       only_complete_fields=False,
   )
   source_columns = list(sirius_details.keys())


   def merge_source_into_target(db_config, target_db):


   	# Get the source data from the 'etl2' schema as a dataframe
       source_data_query = generate_select_query(
           schema=db_config["source_schema"], table=table, columns=source_columns
       )

       source_data_df = pd.read_sql_query(
           con=db_config["db_connection_string"], sql=source_data_query
       )


       # Get the existing data from Sirius in a dataframe
       existing_data_query = generate_select_query(
           schema=db_config["sirius_schema"], table=table, columns=match_columns + ["id"]
       )

       existing_data_df = pd.read_sql_query(
           con=db_config["sirius_db_connection_string"], sql=existing_data_query
       )


       # Merge source data with existing data using the 'match_columns' above
       # 'new' records will have a 'method' of 'INSERT',
       # 'existing' records (any records that match existing data) will have a 'method' of 'UPDATE'
       merged_data_df = merge_source_data_with_existing_data(
           source_data_df, existing_data_df, match_columns
       )


       # Get the next value for the 'id' from the Sirius data and use this to reindex the new records
       new_data_df = reindex_new_data(df=merged_data_df, table=table, db_config=db_config)


       # Insert the new records into the 'integration' schema
       target_db.insert_data(
           table_name=table, df=new_data_df, sirius_details=sirius_details
       )


       # Change the value of 'id' for the existing data to match the record in Sirius
       existing_data = reindex_existing_data(df=merged_data_df, table=table)

       # Insert the existing records into the 'integration' schema
       target_db.insert_data(
           table_name=table, df=existing_data, sirius_details=sirius_details
       )

   ```

4. Edit `migration_steps/integration/merge_with_targer/app/app.py` and add to the `main` method:

   ```python
   	pirates.merge_source_data(db_config=db_config, target_db=target_db)
   ```

#####

##### fk table

1. Add new table to `init.py`

   ```python
       log.info(" - Crew")
       crew.merge_source_into_target(db_config, target_db)
   ```



2. Add a `crew.py` file to the `pirates` folder containing

   ```python
   import json
   import logging
   import os

   import config2
   import pandas as pd
   from helpers import get_mapping_dict

   from merge_helpers import generate_select_query, reindex_new_data, update_foreign_keys

   log = logging.getLogger("root")

   environment = os.environ.get("ENVIRONMENT")
   config = config2.get_config(env=environment)

   row_limit = config.row_limit
   table = "crew"
   fk = {"parent_table": "captains", "parent_col": "id", "fk_col": "captain_id"}


   mapping_file_name = "pirate_crew_mapping"
   sirius_details = get_mapping_dict(
       file_name=mapping_file_name,
       stage_name="sirius_details",
       only_complete_fields=False,
   )
   source_columns = list(sirius_details.keys())


   def merge_source_into_target(db_config, target_db):

       # Get the source data from the 'etl2' schema as a dataframe
       source_data_query = generate_select_query(
           schema=db_config["source_schema"], table=table, columns=source_columns
       )

       source_data_df = pd.read_sql_query(
           con=db_config["db_connection_string"], sql=source_data_query
       )

       # We don't expect to update any existing records here
       # This may vary
       source_data_df["method"] = "INSERT"


       # Get the parent data already inserted into the 'integrations' schema as a dataframe
       fk_data_query = generate_select_query(
           schema=db_config["target_schema"],
           table=fk["parent_table"],
           columns=[fk["parent_col"], f"transformation_{fk['parent_col']}"],
       )

       fk_data_df = pd.read_sql_query(
           con=db_config["db_connection_string"], sql=fk_data_query
       )

       # Reindex new data based on the Sirius ids
       new_data_df = reindex_new_data(df=source_data_df, table=table, db_config=db_config)


       # Reindex based on the existing parent table
       new_data_with_fk_links = update_foreign_keys(
           df=new_data_df, parent_df=fk_data_df, fk_details=fk
       )

       # Insert into 'integrations' schema
       target_db.insert_data(
           table_name=table, df=new_data_with_fk_links, sirius_details=sirius_details
       )

   ```



##### join table

1. Add new table to `init.py`

   ```python
       log.info(" - Crew")
       pirate_Ship.merge_source_into_target(db_config, target_db)
   ```



2. Add a `pirate_ship.py` file to the `pirates` folder containing

   ```python
   import json
   import logging
   import os

   import config2
   import pandas as pd
   from helpers import get_mapping_dict

   from merge_helpers import generate_select_query, reindex_new_data, update_foreign_keys

   log = logging.getLogger("root")

   environment = os.environ.get("ENVIRONMENT")
   config = config2.get_config(env=environment)

   row_limit = config.row_limit
   table = "captain_ships"


   mapping_file_name = "captain_ships_mapping"
   sirius_details = get_mapping_dict(
       file_name=mapping_file_name,
       stage_name="sirius_details",
       only_complete_fields=False,
   )
   source_columns = list(sirius_details.keys())

   captains_table = {
       "table_name": "captains",
       "columns": ["id", "pirate_number"],
       "where": {"type": "swarthy"},
   }
   ship_table = {
       "table_name": "ship",
       "columns": ["id", "pirate_number"],
   }


   def merge_source_into_target(db_config, target_db):


       schema = db_config["target_schema"]
       conn = db_config["db_connection_string"]

       # Get the 'captains' data from the 'integrations' schema as a dataframe
       captains_query = generate_select_query(
           schema=schema,
           table=captains_table["table_name"],
           columns=captains_table["columns"],
           where_clause=captains_table["where"],
       )

       captains_df = pd.read_sql_query(captains_query, conn)


       # Get the 'ship' data from the 'integrations' schema as a dataframe
       ship_query = generate_select_query(
           schema=schema, table=ship_table["table_name"], columns=ship_table["columns"]
       )

       ship_df = pd.read_sql_query(ship_query, conn)


       # Join 'captains' and 'ship' dfs using the common column 'pirate_number'
       captain_ship_df = ship_df.merge(
           pirates_df,
           how="left",
           left_on="pirate_number",
           right_on="pirate_number",
           suffixes=["_crew", "_captain"],
       )

       # Drop join column as it's not required in the final dataset
       pirate_crewitem_df = pirate_crewitem_df.drop(columns=["pirate_number"])

       # Rename the id columns to match the names in Sirius
       pirate_crewitem_df = pirate_crewitem_df.rename(
           columns={"id_crew": "crewitem_id", "id_pirate": "pirate_id"}
       )

       # There  be no updates here arrr
       pirate_crewitem_df["method"] = "INSERT"


       # Insert into the 'integrations' schema
       target_db.insert_data(
           table_name=table, df=pirate_crewitem_df, sirius_details=sirius_details
       )

   ```



#### Load to Staging

    Run independently:
    	migration_steps/integration/load_to_staging/app/app.py

    options:
      --clear=True/False              clear existing data from schema before running
      -v -vv -vvv                     more v's == more detailed logging

###

1. Add the tables you want to move to the `tables.json`. Make sure they are in the right order so the fk relationships still work
2. Verify that you can see the data you expect in the `pre_migration` schema



## Step 3 - Load to Sirius

    Run independently:
    	migration_steps/load_to_sirius/app/app.py

    options:
      -v -vv -vvv                     more v's == more detailed logging

###

1. Add the tables you want to move to the `tables.json`. Make sure they are in the right order so the fk relationships still work
2. Verify that you can see the data you expect in the sirius database



## Step 4 - Validation

tbc