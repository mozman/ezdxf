@ECHO OFF

SET PYTHON=c:\python33\python.exe
IF NOT EXIST %PYTHON% ECHO test33.bat requires Python 3.3

%PYTHON% -m unittest discover -s tests