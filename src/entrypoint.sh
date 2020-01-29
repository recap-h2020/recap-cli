#!/usr/bin/env sh
basedir=$(dirname $0)
module=cli.recap

export PYTHONPATH=${PYTHONPATH}:${basedir}
python3 -m${module} "$@"

