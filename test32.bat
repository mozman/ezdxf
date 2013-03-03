@ECHO OFF

SET PYTHON=c:\python32\python.exe
IF NOT EXIST %PYTHON% ECHO test32.bat requires Python 3.2

%PYTHON% -m unittest discover -s tests