#!/usr/bin/env bash

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
echo "export TF_WORKSPACE=${WORKSPACE}"

VERSION=${VERSION:-$(cat ~/project/VERSION 2>/dev/null)}
echo "export VERSION=${VERSION}"
echo "export TF_VAR_image_tag=${VERSION}"
