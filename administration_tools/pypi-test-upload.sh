#!/bin/bash

# Pypi usage taken from here:
# https://packaging.python.org/guides/using-testpypi/

twine upload --repository testpypi ../dist/*.tar.gz

# Note: install the package from pypi test with:
# pip install --index-url https://test.pypi.org/simple/ EPICS-sumo --prefix PREFIX

