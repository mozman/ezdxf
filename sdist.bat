@ECHO OFF
py setup.py sdist --format=zip %1%
py setup.py bdist_wheel %1%