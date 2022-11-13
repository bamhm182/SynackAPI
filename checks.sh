#!/bin/bash

flake8 src test live-tests

diff_arrays() {
    local -n _one=$1
    local -n _two=$2
    for ((i=0; i<${#_one[@]}; i++)); do
        if [[ "${_one[$i]}" != "${_two[$i]}" ]]; then
            echo -e "${_two[$i]}\t${_one[$i]}"
        fi
    done
}

# Check Plugins
for plugin in ./src/synack/plugins/*.py; do
    p=$(basename ${plugin})
    p=${p%.*}
    defs=($(awk -F'[ (]*' '/ def / {print $3}' ${plugin} | egrep -v "__init__|__init_subclass__|_fk_pragma"))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    # Check Alphabetical
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${plugin} is not in alphabetical order
        diff_arrays defs a_defs
    fi
    # Check Missing Documentation
    for def in ${defs[@]}; do
        grep "## ${p}.${def}" ./docs/src/usage/plugins/${p}.md > /dev/null 2>&1
        if [[ $? != 0 ]]; then
            grep "def ${def}(" ${plugin} -B1 | grep "@property" > /dev/null 2>&1
            if [[ $? != 0 ]]; then
                echo ${p} missing documentation for: ${def}
            fi
        fi
    done
done

# Check Tests
for test in ./test/test_*.py; do
    defs=($(awk -F'[ (]*' '/ def / {print $3}' ${test} | egrep -v "__init__|setUp"))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    # Check Alphabetical
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${test} is not in alphabetical order
        diff_arrays defs a_defs
    fi
done

# Check Docs
for doc in ./docs/src/usage/plugins/*.md; do
    defs=($(awk -F'[ (]*' '/## / {print $2}' ${doc}))
    readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
    # Check Alphabetical
    if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
        echo ${doc} is not in alphabetical order
        diff_arrays defs a_defs
    fi
done

coverage run --source=src --omit=src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py -m unittest discover test
coverage report | egrep -v "^[^T].*100%"
coverage html
