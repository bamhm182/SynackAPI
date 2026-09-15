# Support

I have spent countless hours pouring over this project in order to best help you have an easy, reliable way to interact with the Synack API.

If this has helped you, please consider helping me out in one of the following ways.

## Patreon

You can find my Patreon at the following link:

[BytePen Studios Patreon](https://www.patreon.com/bytepen)

## Contribution

If you'd like to see extra features be added to this package, please consider contributing code.

With that said, please take the following items into consideration:
* We will be using Test Driven Development with Unit Testing in order to ensure the stability of the SynackAPI package.
    * Run `coverage run --source=src --omit='src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py' -m unittest discover test`, then run `coverage report --fail-under=100` before submitting a PR. Ensure that all tests are passing and coverage remains at 100%.
* We will be conforming to pep8, which is the Python Style Guide.
    * Run `flake8 src test` from within the primary directory before submitting a PR. Ensure there are no complaints returned.
* Public plugin methods should be documented.
    * Run `python tools/check_docs.py` to ensure plugin docs match the code.
* We will be trying to break up Functions by their purpose. For example, a function related to examining a mission would go in the Mission plugin.

If you have any questions on how you can contribute, please reach out via the SRT Slack.

