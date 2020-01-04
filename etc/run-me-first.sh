#!/bin/bash
CWD=$(pwd)

if [[ -z "${PROJECT_ROOT}" ]]; then
    PROJECT_ROOT=$(git rev-parse --show-toplevel)
fi
cd $PROJECT_ROOT

[ -d ./common/settings ] || mkdir -p ./common/settings

source ./etc/create_common_template.sh > ./common/settings/__init__.py
export PYTHONPATH=$PROJECT_ROOT/common

cd $CWD
