@ECHO OFF

ECHO Running Python 3.5 tests
CALL test35.bat

ECHO Running pypy tests
CALL testpypy.bat

ECHO Running integration tests
CD integration_tests
py run.py 3.5
py run.py pypy
CD ..