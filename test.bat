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

CD integration_tests
CALL runall.bat 2
CALL runall.bat 3
CALL runall.bat pypy
CD ..