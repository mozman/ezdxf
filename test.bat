@ECHO OFF
ECHO Running Python 2.7 tests
CALL test27.bat
ECHO Running Python 3.2 tests
CALL test32.bat
ECHO Running Python 3.3 tests
CALL test33.bat
ECHO Running pypy tests
CALL testpypy.bat