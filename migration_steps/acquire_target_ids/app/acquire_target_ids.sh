#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${DIR}/../.env" ]
then
  source "${DIR}/../.env"
else
  echo "no env file, using normal env vars"
fi

export PGPASSWORD=${DB_PASSWORD}
pg_dump -U ${DB_USER} -n etl2 -h ${DB_HOST} -p ${DB_PORT} ${DB_NAME} > "${DIR}/etl2.sql"
cat "${DIR}/etl2.sql" | sed 's/etl2/etl3/' | sed 's/CREATE SCHEMA etl3;/DROP SCHEMA IF EXISTS etl3 CASCADE; CREATE SCHEMA etl3;/' > "${DIR}/etl3.sql"
psql -U ${DB_USER} -h ${DB_HOST} -p ${DB_PORT} ${DB_NAME} < "${DIR}/etl3.sql"
psql -U ${DB_USER} -h ${DB_HOST} -p ${DB_PORT} ${DB_NAME} < "${DIR}/sql/sirius_id_cols.sql"
python3 "${DIR}/fixtures.py"
python3 "${DIR}/app.py"
