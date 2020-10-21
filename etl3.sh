#!/bin/bash
echo '-- Building DB containers --';
docker-compose up --no-deps -d casrec_db postgres-sirius
docker-compose run --rm wait-for-it -address casrec_db:5432 --timeout=30 -debug
docker-compose run --rm wait-for-it -address postgres-sirius:5432 --timeout=30 -debug
docker-compose up --no-deps -d casrec_db postgres-sirius-restore

echo '-- Build ETL3 schema from a fresh copy of etl2 schema --'
rm db-snapshots/etl2.sql
rm db-snapshots/etl3.sql
docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME pg_dump -U $DB_CASRECMIGRATION_USER -n etl2 $DB_CASRECMIGRATION_NAME > db-snapshots/etl2.sql
cat db-snapshots/etl2.sql | sed 's/etl2/etl3/' | sed 's/CREATE SCHEMA etl3;/DROP SCHEMA IF EXISTS etl3 CASCADE; CREATE SCHEMA etl3;/' > db-snapshots/etl3.sql
docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME psql -U $DB_CASRECMIGRATION_USER $DB_CASRECMIGRATION_NAME < db-snapshots/etl3.sql

echo '-- Modify ETL3 schema --'
docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME psql -U $DB_CASRECMIGRATION_USER $DB_CASRECMIGRATION_NAME < etl3/sql/sirius_id_cols.sql

echo '-- Running ETL3 transform --'
python3 etl3/app.py


export DB_CASRECMIGRATION_HOST=localhost
export DB_CASRECMIGRATION_PORT=6666
export DB_CASRECMIGRATION_NAME=casrecmigration
export DB_CASRECMIGRATION_USER=casrec  # pragma: allowlist secret
export DB_CASRECMIGRATION_PASSWORD=casrec  # pragma: allowlist secret

pg_dump -U casrec -n etl2 -h casrec_db:5432 casrecmigration > db-snapshots/etl2.sql
