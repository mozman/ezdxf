import sys
from subprocess import call
from pathlib import Path

# install ezdxf editable for pypy:
# pypy -m pip install -e ezdxf.git

# install ezdxf editable for Python 3:
# pip install -e ezdxf.git

WINDOWS = sys.platform.startswith('win')

if len(sys.argv) > 1:
    python_version = sys.argv[1]
else:
    if WINDOWS:
        python_version = '3.6'  # default python version for py.exe
    else:
        python_version = 'python'

if WINDOWS:
    if python_version.startswith('pypy'):
        cmd = python_version+'.bat'
    else:  # run py.exe command on Windows
        cmd = 'py'
else:
    cmd = python_version  # call executable as 'python' (1. command line arg)

for test_file in Path().glob('*.py'):
    if test_file.name == __file__:  # do not run 'run.py'
        continue
    if test_file.name.startswith('test_'):  # executed by pytest
        continue
    if cmd == 'py':  # py.exe can run different Python versions
        call([cmd, '-'+python_version, str(test_file)])
    else:
        call([cmd, str(test_file)])

