#!/bin/bash
set -e
while getopts i: option
do
  case "${option}"
  in
    i) IGNORE=${OPTARG};;
    *) echo "usage: $0 [-i]" >&2
           exit 1 ;;
  esac
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 "${DIR}/prepare_target/app/app.py" --ignore_schemas="${IGNORE}"
python3 "${DIR}/create_stage_schema/app/app.py"
