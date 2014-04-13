@ECHO OFF

ECHO Running Python 2.7 tests
CALL test27.bat
ECHO Running Python 3.3 tests
CALL test33.bat
ECHO Running Python 3.4 tests
CALL test34.bat
ECHO Running pypy tests
CALL testpypy.bat
REM ECHO Running pypy3 tests
REM CALL testpypy3.bat

CD integration_tests
CALL runall.bat 2
CALL runall.bat 3
CALL runall.bat pypy
CD ..