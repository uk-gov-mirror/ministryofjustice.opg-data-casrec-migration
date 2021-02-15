#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 "${DIR}/schema_setup/app/app.py"
#python3 "${DIR}/fixtures/app/app.py"
python3 "${DIR}/merge_with_target/app/app.py" -vv --clear=True
python3 "${DIR}/load_to_staging/app/app.py" -vv --clear=True

