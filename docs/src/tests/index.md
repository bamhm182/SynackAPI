# Tests

Honestly, this section is not for most people.
It explains how to run the tests to ensure that the code is working or to help in writing new functionality for SynackAPI.

## Unit Tests

These tests are run by me repeatedly while developing the package, and every time that I push to the repository.
They are then run again every time that I tell my GitHub workflow to go release a new version.
If things fail, a new version is not released.

That said, you can run them using the `checks.sh` script in the main folder.

## Live Tests

These tests are run manually and sparingly.
They ensure that Synack has not changed any of their API endpoints in ways we are not expecting.
If these tests fail, it is very possible that I will need to go in and change some functionality of the SynackAPI so they continue to work as expected.

If you run these, they SHOULD be relatively quiet, but keep in mind that they also might not.
In other words, make sure you have not been heavily using the Synack API when you run these.

These tests can be run via something like the following for a single test:

```
coverage run -m unittest live-tests.test_missions.MissionsTestCase
```

You can also run the following for all live tests:

```
coverage run -m unittest discover live-tests
```
