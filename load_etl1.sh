#!/bin/bash
docker-compose up --no-deps -d casrec_db localstack
docker-compose run --rm wait-for-it -address casrec_db:5432 --timeout=30 -debug
docker-compose run --rm load_s3 python3 load_s3_local.py
docker-compose run --rm load_casrec python3 casrec_load.py
