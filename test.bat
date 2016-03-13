@ECHO OFF

ECHO Running Python 2.7 tests
CALL test27.bat
ECHO Running Python 3.4 tests
CALL test34.bat
ECHO Running Python 3.5 tests
CALL test35.bat

ECHO Running pypy tests
CALL testpypy.bat
ECHO Running pypy3 tests
CALL testpypy3.bat

ECHO Running integration tests
CD integration_tests
py run.py 2.7
py run.py 3.5
py run.py pypy
CD ..