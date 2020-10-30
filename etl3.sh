# This should no longer be needed but will check with JG

##!/bin/bash
#$(cat acquire_target_ids/app/.envrc)
#
#echo '-- Building DB containers --';
#docker-compose up --no-deps -d casrec_db postgres-sirius
#docker-compose run --rm wait-for-it -address casrec_db:5432 --timeout=30 -debug
#docker-compose run --rm wait-for-it -address postgres-sirius:5432 --timeout=30 -debug
#docker-compose up --no-deps -d casrec_db postgres-sirius-restore
#
#echo '-- Build ETL3 schema from a fresh copy of transform_casrec schema --'
#rm db-snapshots/transform_casrec.sql
#rm db-snapshots/acquire_target_ids.sql
#docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME pg_dump -U $DB_CASRECMIGRATION_USER -n transform_casrec $DB_CASRECMIGRATION_NAME > db-snapshots/transform_casrec.sql
#cat db-snapshots/transform_casrec.sql | sed 's/transform_casrec/acquire_target_ids/' | sed 's/CREATE SCHEMA acquire_target_ids;/DROP SCHEMA IF EXISTS acquire_target_ids CASCADE; CREATE SCHEMA acquire_target_ids;/' > db-snapshots/acquire_target_ids.sql
#docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME psql -U $DB_CASRECMIGRATION_USER $DB_CASRECMIGRATION_NAME < db-snapshots/acquire_target_ids.sql
#
#echo '-- Modify ETL3 schema --'
#docker exec -i $DOCKER_CASRECDB_CONTAINER_NAME psql -U $DB_CASRECMIGRATION_USER $DB_CASRECMIGRATION_NAME < acquire_target_ids/sql/sirius_id_cols.sql
#
#echo '-- Add some fixtures to Sirius --'
#python3 fixtures/app.py
#
#echo '-- Running ETL3 transform --'
#python3 acquire_target_ids/app.py
