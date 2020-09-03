#!/bin/bash
docker-compose up --no-deps -d postgres-api
docker-compose run --rm wait-for-it -address postgres-api:5432 --timeout=30 -debug
docker-compose run --rm postgres-api-restore > .pg_restore.api.log