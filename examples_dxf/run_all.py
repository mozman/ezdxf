#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import subprocess

PYTHON3 = "python3"


def main():
    filepath = Path(__file__)
    for script in filepath.parent.glob("create_*.py"):
        cmd = f"{PYTHON3} {script}"
        print(f'executing: "{cmd}"')
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
