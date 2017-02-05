import sys
import os
import glob
from subprocess import call


os.environ['PYTHONPATH'] = os.path.abspath(os.path.pardir)  # set PYTHONPATH to developer version of ezdxf
print("PYTHONPATH={}".format(os.environ['PYTHONPATH']))
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

for test_file in glob.glob('*.py'):
    if test_file.endswith(__file__):
        continue
    if cmd == 'py':  # py.exe can run different Python versions
        call([cmd, '-'+python_version, test_file])
    else:
        call([cmd, test_file])

