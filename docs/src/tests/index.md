# Tests

Honestly, this section is not for most people.
It explains how to run the tests to ensure that the code is working or to help in writing new functionality for SynackAPI.

## Unit Tests

These tests are run repeatedly while developing the package, on pushes, and before releases.
If things fail, a new version is not released.

To run the unit tests directly:

```
coverage run --source=src --omit='src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py' -m unittest discover test
coverage report --fail-under=100
```

## Documentation Checks

Public plugin methods are checked against the plugin documentation. To run that check directly:

```
python tools/check_docs.py
```
