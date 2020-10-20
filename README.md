# opg-data-casrec-migration

## Purpose

The purpose of this repo is to house all the code that we will use to perform the casrec to sirius migration.
Having investigated AWS Glue & pyspark, we are using pandas dataframes to transform the data set into a form that can then be
injested / inserted into Sirius platform.

We use AWS Localstack and postgres containers locally

## <u>How to do things</u>
=======
## Setup from scratch

All commands are from the root directory of `opg-data-casrec-migration` unless otherwise stated

```bash
git clone git@github.com:ministryofjustice/opg-data-casrec-migration.git
cd opg-data-casrec-migration
direnv allow
```

Create and activate python virtual environment

```bash
virtualenv venv
source venv/bin/activate

which python
> ...opg-data-casrec-migration/venv/bin/python
```

Install python requirements

```bash
pip install -r etl1/requirements.txt
pip install -r etl2/requirements.txt
```

### Before you start

For development we have a sample set of migration data in the same format as the files we will be receiving from Casrec (about 40 files).
Sensitive data has been removed - hence we call this our 'anonymised csv data'.

You need to save these files to `etl1/anon_data/` on your development machine

```bash
mkdir -p etl1/anon_data
```

However these files are not currently hosted anywhere - see a member of the team for a zip of csv docs to work with. Unzip the docs under etl1/anon_data/*.csv (about 40 files)

## ETL

'ETL' means Extract, Transform, Load but we are building a series of smaller data transform steps, so it's more like ETTTT(...)L

```
E - (etl1) the data is extracted from its home on S3 and loaded into postgres etl1 schema by etl1/casrec_load.py
T - (etl2) the data is transformed by etl2/transformations
T - (etl3) row IDs from the Sirius Database are identified and merged in with the corresponding data
T - ...probably other  transformations
T - ...
L - import into Sirius
```

## ETL 1 and ETL2 (and build Docker containers)

To mimic what happens in AWS, we load up a localstack S3 service with the anonymised CSV data and then have a container (with the same build as ECS task in AWS) that runs the scripts in to the etl1 schema in casrec.

```bash
./load_etl1.sh
```

Or do the steps individually:

```bash
# 1. Build docker containers for casrec_db and AWS localstack
docker-compose up --no-deps -d casrec_db localstack

# 2. Load the files in etl1/anon_data/*.csv into localstack S3
docker-compose run --rm load_s3 python3 load_s3_local.py

# 3. (ETL1) Import the csv files into a postgres schema (called etl1) which matches the casrec file structure
docker-compose run --rm load_casrec python3 casrec_load.py
For development purposes you can also run this from the command line as it uses direnv file to make it runnnable both inside and outside of docker:
cd etl1 (direnv will load correct env vars)
python3 casrec_load.py

# 4. (ETL2) cd etl2/app && direnv allow && python3 app.py
```

## ETL3

ETL3 takes the data output of ETL2 and combines with data from the Sirius DB. For development we therefore build a local instance of the Sirius DB, rebuilt from a backup taken from a Sirius dev environment (normally the result of running `make ingest` in that project)

There is NO requirement to run a full instance of Sirius on your development machine, but _get a hold of a DB backup from that team and make sure it is saved to `sb-snapshots/api.backup`_

```bash
./etl3.sh
```

## DB connections for clients eg PyCharm and DataGrip:
```
db:   casrecmigration
host: localhost
port: 6666
user: casrec
pass: casrec
schema: etl1

db:   sirius
host: localhost
port: 5555
user: api
pass: api
schema: etl2
```

If you don't see the tables in datagrip/pycharm db client, go across to 'schemas' and check that you have all necessary schemas checked (in this case `etl1`)
