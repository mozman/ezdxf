@echo off
cd ..
set PYTHONPATH=%CD%
cd integration_tests
echo PYTHONPATH=%PYTHONPATH%

for %%e in (*.py) do py -3 %%e