#!/bin/bash
set -e
while getopts s: option
do
  case "${option}"
  in
    s) SYNC=${OPTARG};;
    *) echo "usage: $0 [-s]" >&2
           exit 1 ;;
  esac
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "${SYNC}" == "TRUE" ]
then
  python3 "${DIR}/synchronise_s3.py"
fi
python3 "${DIR}/load_s3_local.py"
