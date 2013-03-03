@ECHO OFF

SET PYTHON=c:\python27\python.exe
IF NOT EXIST %PYTHON% ECHO test27.bat requires Python 2.7

%PYTHON% -m unittest discover -s tests