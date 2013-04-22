@ECHO OFF
SET ver=%1
IF "%ver%" == "" SET ver=3.3

ECHO ---------------------------------------------------
ECHO Integration tests for Python version: %ver%
CD ..
SET PYTHONPATH=%CD%
CD integration_tests

IF %ver% == pypy (
    SET cmd=call pypy.bat
) ELSE (
    SET cmd=py -%ver%
)

FOR %%e IN (*.py) DO (
    ECHO running: %%e
    %cmd% %%e
)