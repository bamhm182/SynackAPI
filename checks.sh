#!/bin/bash

flake8 src test live-tests
coverage run --source=src --omit=src/synack/db/alembic/env.py,src/synack/db/alembic/versions/649443e08834_initial.py -m unittest discover test
coverage report | egrep -v "^[^T].*100%"
coverage html
