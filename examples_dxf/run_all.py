#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import subprocess
import shlex
import shutil
import sys

PYTHON3 = "python3"
POSIX = sys.platform != "win32"
if POSIX:
    PYTHON3 = shutil.which(PYTHON3)


def main():
    filepath = Path(__file__)
    for script in filepath.parent.glob("create_*.py"):
        cmd = f"{PYTHON3} {script}"
        print(f'executing: "{cmd}"')
        args = shlex.split(cmd, posix=POSIX)
        subprocess.run(args)


if __name__ == "__main__":
    main()
