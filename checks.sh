#!/bin/bash

flake8 src test live-tests
coverage run --source=src --omit=src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py -m unittest discover test
coverage report | egrep -v "^[^T].*100%"
coverage html

for plugin in ./src/synack/plugins/*.py; do
    p=$(basename ${plugin})
    p=${p%.*}
    defs=$(awk -F'[ (]*' '/def/ {print $3}' ${plugin} | egrep -v "__init|_fk_pragma")
    for def in ${defs}; do
        grep "## ${p}.${def}" ./docs/src/usage/plugins/${p}.md > /dev/null 2>&1
        if [[ $? != 0 ]]; then
            grep "def ${def}(" ${plugin} -B1 | grep "@property" > /dev/null 2>&1
            if [[ $? != 0 ]]; then
                echo ${p} missing documentation for: ${def}
            fi
        fi
    done
done
