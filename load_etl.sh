#!/bin/bash
docker-compose up --no-deps -d casrec_db localstack postgres-sirius
docker-compose run --rm wait-for-it -address postgres-sirius:5432 --timeout=30 -debug
docker-compose up --no-deps -d postgres-sirius-restore
docker-compose run --rm wait-for-it -address casrec_db:5432 --timeout=30 -debug
docker-compose run --rm load_s3 python3 load_s3_local.py
docker rm casrec_load_1 || echo "casrec_load_1 does not exist"
docker rm casrec_load_2 || echo "casrec_load_2 does not exist"
docker rm casrec_load_3 || echo "casrec_load_3 does not exist"
docker rm casrec_load_4 || echo "casrec_load_4 does not exist"
docker-compose run --rm --name casrec_load_1 load_casrec python3 casrec_load.py >> docker_load.log &
P1=$!
docker-compose run --rm --name casrec_load_2 load_casrec python3 casrec_load.py >> docker_load.log &
P2=$!
docker-compose run --rm --name casrec_load_3 load_casrec python3 casrec_load.py >> docker_load.log &
P3=$!
docker-compose run --rm --name casrec_load_4 load_casrec python3 casrec_load.py >> docker_load.log &
P4=$!
wait $P1 $P2 $P3 $P4
cat docker_load.log
rm docker_load.log
docker-compose run --rm transform_casrec python3 app.py --clear=True
docker-compose run --rm rationalise ./run_rationalise.sh
