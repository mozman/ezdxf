#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest
from pathlib import Path
import subprocess

# Got errors at github actions for ubuntu-latest:
# Error was using (works on Windows):
#       subprocess.run("ezdxf -V")
#
# This works on Linux and Windows:
#       subprocess.run(["ezdxf", "-V"])

TEST_DATA = Path(__file__).parent / "data"
CRLF = b'\r\n'


def test_version():
    result = subprocess.run(["ezdxf", "-V"],
                            capture_output=True)
    assert result.returncode == 0
    assert result.stdout.startswith(b'ezdxf')


def test_audit_existing_file():
    result = subprocess.run(
        ["ezdxf", "audit", str(TEST_DATA / "POLI-ALL210_12.DXF")],
        capture_output=True)
    assert result.returncode == 0
    assert result.stdout.rstrip(CRLF).endswith(b"No errors found.")


def test_audit_file_not_found():
    result = subprocess.run(["ezdxf", "audit", "nofile.dxf"],
                            capture_output=True)
    assert result.returncode == 0
    assert result.stderr.rstrip(CRLF) == b"File(s) 'nofile.dxf' not found."


if __name__ == '__main__':
    pytest.main([__file__])
