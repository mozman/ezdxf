# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import string
import time
from ezdxf.path import Path2d, Command
from ezdxf.npshapes import NumpyPath2d
from ezdxf.fonts import fonts


def get_text_path():
    f = fonts.make_font("DejaVuSans.ttf", 1.0)
    return f.text_path(string.ascii_letters)


LARGE_PATH = get_text_path()
NP_PATH_2D = NumpyPath2d(LARGE_PATH)


def regular_to_path2d(np_path_2d: NumpyPath2d) -> Path2d:
    """Replaced method for :class:`NumpyPath2d` to :class:`Path2d` conversion, slow but
    uses only public methods of the Path2d class.
    """
    v = np_path_2d._vertices
    if len(v) == 0:
        return Path2d()
    path = Path2d(v[0])
    index = 1
    for command in np_path_2d._commands:
        if command == Command.MOVE_TO:
            path.move_to(v[index])
            index += 1
        elif command == Command.LINE_TO:
            path.line_to(v[index])
            index += 1
        elif command == Command.CURVE3_TO:
            path.curve3_to(v[index + 1], v[index])
            index += 2
        elif command == Command.CURVE4_TO:
            path.curve4_to(v[index + 2], v[index], v[index + 1])
            index += 3
        else:
            raise ValueError(f"invalid command: {command}")
    return path


def regular_np_path_2d_conversion():
    regular_to_path2d(NP_PATH_2D)


def fast_np_path_2d_conversion():
    NP_PATH_2D.to_path2d()


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 1000

print(f"Profiling NumpyPath2d to Path2d conversion:")
print(
    f"Test path has {len(LARGE_PATH)} commands and {len(LARGE_PATH.control_vertices())} control vertices."
)
profile(f"regular_np_path_2d_conversion() {RUNS}:", regular_np_path_2d_conversion, RUNS)
profile(f"fast_np_path_2d_conversion() {RUNS}:", fast_np_path_2d_conversion, RUNS)
