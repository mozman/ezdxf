@ECHO OFF
py setup.py sdist --format=zip
py setup.py bdist_wheel
