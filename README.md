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

## Before you start

For development we have a sample set of migration data in the same format as the files we will be receiving from Casrec (about 40 files).
Sensitive data has been removed - hence we call this our 'anonymised csv data'.

You need to save these files to `etl1/anon_data/` on your development machine

```bash
mkdir -p etl1/anon_data
```

However these files are not currently hosted anywhere - see a member of the team for a zip of csv docs to work with. Unzip the docs under etl1/anon_data/*.csv (about 40 files)

### Install Sirius project (optional)
In order to see the results of a migration in the Sirius Front end you'll need the actual Sirius project:

Installing Sirius in a nutshell (refer to Sirius docs for more):

```
git clone git@github.com:ministryofjustice/opg-sirius.git
cd opg-sirius

# authenticate with AWS (get ops to help you set this up if you haven't got aws-vault)
aws-vault exec sirius-dev-operator -- make ecr_login

make clean && make dev-setup
# (you can re-run make dev-setup if it fails, without doing a make-clean)
```

You should be able to view Sirius FE at http://localhost:8080
You should also be able to log in as case.manager@opgtest.com / Password1

If you can't log in, or if the site doesn't appear at all, but your containers seem to be up ok, It sometimes helps to turn it off and on again:

```
make dev-stop
make dev-up
```

You now need to take down the S3 localstack container because it conflicts with ours

```
docker stop opg-sirius_localstack-s3_1
```


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
./load_etl.sh
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

# 4. (ETL2) cd etl2/app && direnv allow && python3 app.py --clear=True
```

## ETL3 (also loads fixtures onto Sirius)

ETL3:
 - dumps the ETL2 DB schema to `db-snapshots/etl2.sql`
 - drops the ETL3 schema, then rebuilds it from ETL2, with new table columns added to take some Sirius ids
 - grabs sirius IDs into map tables (eg `sirius_map_persons` maps sirius's persons.id against the casrec number)
 - uses the maps to import the sirius ids alongside the etl ids into the main tables (eg `persons`)
 - Loads the first 10 clients into Sirius DB to represent the Skeleton clients that exist on real Sirius. The fields populated in Sirius are an accurate representation of a skeleton record. The following is inserted:
    - 10 persons (clients)
    - 10 addresses belonging to those persons
    - 5 persons' worth of cases

```bash
./etl3.sh
```

## Load

```
./load.sh
```

## Re-index Sirius

Once we've migrated across some data, have Sirius re-index its search, so we can search for the new stuff in the search bar

```
(In Sirius local dev root)
docker-compose run --rm queue scripts/elasticsearch/setup.sh
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

db:   sirius project postgres
host: localhost
port: 5432
user: api
pass: api
schema: public
```

If you don't see the tables in datagrip/pycharm db client, go across to 'schemas' and check that you have all necessary schemas checked (in this case `etl1`)

## Reset DB fixtures
wget https://github.com/ministryofjustice/opg-ecs-helper/releases/download/v0.2.0/opg-ecs-helper_Linux_x86_64.tar.gz -O $HOME/opg-ecs-helper.tar.gz
wget https://github.com/ministryofjustice/opg-ecs-helper/releases/download/v0.2.0/opg-ecs-helper_Darwin_x86_64.tar.gz -O $HOME/opg-ecs-helper.tar.gz
sudo tar -xvf $HOME/opg-ecs-helper.tar.gz -C /usr/local/bin
sudo chmod +x /usr/local/bin/ecs-stabilizer
sudo chmod +x /usr/local/bin/ecs-runner
cd environment
export TF_WORKSPACE=casmigrate
ecs-runner -task reset-api -timeout 600
ecs-runner -task migrate-api -timeout 600
ecs-runner -task import-fixtures-api -timeout 600
