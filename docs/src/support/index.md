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
    * Run `coverage run -m unittest discover test` from within the primary directory, then run `coverage report` before submitting a PR. Ensure that all tests are passing and the test coverage reports 100%.
* We will be conforming to pep8, which is the Python Style Guide.
    * Run `flake8 src test live-tests` from within the primary directory before submitting a PR. Ensure there are no complaints returned.
* We will be trying to break up Functions by their purpose. For example, a function related to examining a mission would go in the Mission plugin.

There is also the `./check.sh` script in the primary directory that will run everything I would like you to check before submitting a PR.

If you have any questions on how you can contribute, please reach out via the SRT Slack.

