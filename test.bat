@ECHO OFF
ECHO ********************************************************
ECHO Running Python 3.6 tests
ECHO ********************************************************
CALL test36.bat

ECHO ********************************************************
ECHO Running Python 3.7 tests
ECHO ********************************************************
CALL test37.bat

ECHO ********************************************************
ECHO Running pypy3 tests
ECHO ********************************************************
CALL testpypy3.bat

ECHO ********************************************************
ECHO Running Python 3.6 integration tests with pytest
ECHO ********************************************************
pytest integration_tests

ECHO ********************************************************
ECHO Running pypy3 integration tests with pytest
ECHO ********************************************************
pypy3 -m pytest integration_tests
