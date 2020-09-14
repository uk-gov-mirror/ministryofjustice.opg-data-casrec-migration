# opg-data-casrec-migration

## Purpose

The purpose of this repo is to house all the code that we will use to perform the casrec to sirius migration.
The original discovery recommended AWS Glue & pyspark to transform the data set into a form that can then be
injested / inserted into Sirius platform.

However our approach (as well as this readme) will develop over time!



## <u>How to do things</u>

### Run the Sirius DB locally (and access it through PyCharm)

1. `docker-compose up --build`
2. Pycharm `databases` tab
3. `+` -> `data source` -> `PostGres`
4. set the name (I would suggest `sirius_datbase`)
5. Host: `localhost`
6. User: `api`
7. Password: `api`
8. Click `Test Connection` and it should give you a little green tick
9. Now behold, the db is over there in the `databases` tab ready for you to work on

