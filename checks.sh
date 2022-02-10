#!/bin/bash

flake8 src test live-tests
coverage run -m unittest discover test
coverage report | grep -v "100%"
coverage html
