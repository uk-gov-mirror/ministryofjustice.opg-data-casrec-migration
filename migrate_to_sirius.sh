#!/bin/bash
set -e
docker build base_image -t opg_casrec_migration_base_image:latest
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml up --no-deps -d casrec_db localstack
sleep 10
docker-compose -f docker-compose.sirius.yml run --rm wait-for-it -address casrec_db:5432 --timeout=30 -debug
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm load_s3 python3 load_s3_local.py
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm prepare prepare/prepare.sh -i "${SKIP_SCHEMAS}"
docker rm casrec_load_1 &>/dev/null || echo "casrec_load_1 does not exist. This is OK"
docker rm casrec_load_2 &>/dev/null || echo "casrec_load_2 does not exist. This is OK"
docker rm casrec_load_3 &>/dev/null || echo "casrec_load_3 does not exist. This is OK"
docker rm casrec_load_4 &>/dev/null || echo "casrec_load_4 does not exist. This is OK"
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm --name casrec_load_1 load_casrec python3 app.py --delay=0 --skip_load="${SKIP_LOAD}" >> docker_load.log &
P1=$!
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm --name casrec_load_2 load_casrec python3 app.py --delay=2 --skip_load="${SKIP_LOAD}" >> docker_load.log &
P2=$!
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm --name casrec_load_3 load_casrec python3 app.py --delay=3 --skip_load="${SKIP_LOAD}" >> docker_load.log &
P3=$!
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm --name casrec_load_4 load_casrec python3 app.py --delay=4 --skip_load="${SKIP_LOAD}" >> docker_load.log &
P4=$!
wait $P1 $P2 $P3 $P4
cat docker_load.log
rm docker_load.log
echo "=== Step 1 - Transform ==="
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm transform_casrec transform_casrec/transform.sh --clear=True
echo "=== Step 2 - Integrate with Sirius ==="
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm integration integration/integration.sh
echo "=== Step 3 - Validate Staging ==="
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm validation python3 /validation/validate_db/app/app.py --staging
echo "=== Step 4 - Load to Sirius ==="
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm load_to_target  load_to_sirius/load_to_sirius.sh
echo "=== Step 5 - Validate Sirius ==="
docker-compose -f docker-compose.sirius.yml -f docker-compose.override.yml run --rm validation validation/validate.sh "$@"