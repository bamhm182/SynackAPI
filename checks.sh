#!/bin/bash

flake8 src test live-tests

for plugin in ./src/synack/plugins/*.py; do
    p=$(basename ${plugin})
    p=${p%.*}
    defs=($(awk -F'[ (]*' '/ def / {print $3}' ${plugin} | egrep -v "__init__|_fk_pragma"))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${plugin} is not in alphabetical order
        echo -e "\tBad:  ${defs[@]}"
        echo -e "\tGood: ${a_defs[@]}"
    fi
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

for test in ./test/test_*.py; do
    defs=($(awk -F'[ (]*' '/ def / {print $3}' ${test} | egrep -v "__init__|setUp"))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${test} is not in alphabetical order
        echo -e "\tBad:  ${defs[@]}"
        echo -e "\tGood: ${a_defs[@]}"
    fi
done

for doc in ./docs/src/usage/plugins/*.md; do
    defs=($(awk -F'[ (]*' '/## / {print $2}' ${doc}))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${doc} is not in alphabetical order
        echo -e "\tBad:  ${defs[@]}"
        echo -e "\tGood: ${a_defs[@]}"
    fi
done

coverage run --source=src --omit=src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py -m unittest discover test
coverage report | egrep -v "^[^T].*100%"
coverage html
