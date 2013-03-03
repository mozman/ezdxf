@ECHO OFF

SET PYTHON=c:\pypy-2.0-beta1\pypy.exe
IF NOT EXIST %PYTHON% ECHO testpypy.bat requires pypy-2.0-beta1

%PYTHON% -m unittest discover -s tests