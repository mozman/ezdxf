#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List
from pathlib import Path
import enum
import platform
import shutil
import subprocess
from uuid import uuid4
import tempfile

from ezdxf.render import MeshBuilder, MeshTransformer
from ezdxf.addons import meshex

DEFAULT_WIN_OPENSCAD_PATH = r"C:\Program Files\OpenSCAD\openscad.exe"
CMD = "openscad"


class Operation(enum.Enum):
    union = 0
    difference = 1
    intersection = 2


UNION = Operation.union
DIFFERENCE = Operation.difference
INTERSECTION = Operation.intersection


def get_openscad_path() -> str:
    if platform.system() in ("Linux", "Darwin"):
        return CMD
    else:
        return DEFAULT_WIN_OPENSCAD_PATH


def is_installed() -> bool:
    f"""Returns ``True`` if OpenSCAD is installed. On Windows only the
    default install path '{DEFAULT_WIN_OPENSCAD_PATH}' is checked.
    """
    if platform.system() in ("Linux", "Darwin"):
        return shutil.which(CMD) is not None
    return Path(DEFAULT_WIN_OPENSCAD_PATH).exists()


def run(script: str, prg: str = None) -> MeshTransformer:
    """Executes the given `script` by OpenSCAD and returns the result mesh as
    :class:`~ezdxf.render.MeshTransformer`.
    """
    if prg is None:
        prg = get_openscad_path()

    workdir = Path(tempfile.gettempdir())
    uuid = str(uuid4())
    # The OFF format is more compact than the default STL format
    off_path = workdir / f"ezdxf_{uuid}.off"
    scad_path = workdir / f"ezdxf_{uuid}.scad"

    scad_path.write_text(script)
    subprocess.call(
        [
            prg,
            "--quiet",
            "-o",
            str(off_path),
            str(scad_path),
        ]
    )
    # Remove the OpenSCAD temp file:
    scad_path.unlink(missing_ok=True)

    new_mesh = MeshTransformer()
    # Import the OpenSCAD result from OFF file:
    if off_path.exists():
        new_mesh = meshex.off_loads(off_path.read_text())

    # Remove the OFF temp file:
    off_path.unlink(missing_ok=True)
    return new_mesh


class Script:
    def __init__(self):
        self.data: List[str] = []

    def add(self, data: str) -> None:
        self.data.append(data)

    def begin_block(self):
        self.add("{")

    def end_block(self):
        self.add("}")

    def add_mesh(self, mesh: MeshBuilder) -> None:
        self.add(meshex.scad_dumps(mesh))

    def get_string(self) -> str:
        return "\n".join(self.data) + "\n"


def boolean_operation(
    op: Operation, mesh1: MeshBuilder, mesh2: MeshBuilder
) -> str:
    assert isinstance(op, Operation), "Operation() enum expected"
    script = Script()
    script.add(f"{op.name}()")
    script.begin_block()
    script.add_mesh(mesh1)
    script.add_mesh(mesh2)
    script.end_block()
    return script.get_string()
