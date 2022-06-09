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

from ezdxf.math import Matrix44
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
    r"""Returns ``True`` if OpenSCAD is installed. On Windows only the
    default install path 'C:\\Program Files\\OpenSCAD\\openscad.exe' is checked.
    """
    if platform.system() in ("Linux", "Darwin"):
        return shutil.which(CMD) is not None
    return Path(DEFAULT_WIN_OPENSCAD_PATH).exists()


def run(script: str, exec_path: str = None) -> MeshTransformer:
    """Executes the given `script` by OpenSCAD and returns the result mesh as
    :class:`~ezdxf.render.MeshTransformer`.

    Args:
        script: the OpenSCAD script as string
        exec_path: path to the executable as string or ``None`` to use the
            default installation path

    """
    if exec_path is None:
        exec_path = get_openscad_path()

    workdir = Path(tempfile.gettempdir())
    uuid = str(uuid4())
    # The OFF format is more compact than the default STL format
    off_path = workdir / f"ezdxf_{uuid}.off"
    scad_path = workdir / f"ezdxf_{uuid}.scad"

    scad_path.write_text(script)
    subprocess.call(
        [
            exec_path,
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


def str_matrix44(m: Matrix44) -> str:
    # OpenSCAD uses column major order!
    s = ", ".join([str(list(c)) for c in m.columns()])
    return f"[{s}]"


class Script:
    def __init__(self):
        self.data: List[str] = []

    def add(self, data: str) -> None:
        """Add a string."""
        self.data.append(data)

    def add_polyhedron(self, mesh: MeshBuilder) -> None:
        """Add `mesh` as polyhedron() entity."""
        self.add(meshex.scad_dumps(mesh))

    def add_multmatrix(self, m: Matrix44):
        """Add a transformation matrix of type :class:`~ezdxf.math.Matrix44` as
        ``multmatrix()`` operation."""
        self.add(f"multmatrix(m = {str_matrix44(m)})")  # no pending ";"

    def get_string(self) -> str:
        """Returns the OpenSCAD build script. """
        return "\n".join(self.data)


def boolean_operation(
    op: Operation, mesh1: MeshBuilder, mesh2: MeshBuilder
) -> str:
    """Returns an `OpenSCAD`_ script to apply the given boolean operation to the
    given meshes.

    The supported operations are:

        - UNION
        - DIFFERENCE
        - INTERSECTION

    """
    assert isinstance(op, Operation), "enum of type Operation expected"
    script = Script()
    script.add(f"{op.name}() {{")
    script.add_polyhedron(mesh1)
    script.add_polyhedron(mesh2)
    script.add("}")
    return script.get_string()
