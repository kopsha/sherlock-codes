#!/bin/bash
set -e

CWD=$(pwd)

PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd $PROJECT_ROOT

[ -d ./common/settings ] || mkdir -p ./common/settings

echo "export PYTHONPATH=$PROJECT_ROOT/common"
source ./etc/create_common_template.sh > ./common/settings/__init__.py

cd $CWD
