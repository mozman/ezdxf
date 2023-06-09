# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import string
import time
from ezdxf.npshapes import NumpyPath2d
from ezdxf.path import Path2d
from ezdxf.fonts import fonts


def get_glyph_paths():
    f = fonts.make_font("DejaVuSans.ttf", 1.0)
    return [f.text_path(char) for char in string.ascii_letters]


PATH_2D = get_glyph_paths()
NP_PATH_2D = [NumpyPath2d(p) for p in PATH_2D]


def concat_np_paths():
    NumpyPath2d.concatenate(NP_PATH_2D)


def concat_2d_paths_to_np_path():
    NumpyPath2d.concatenate([NumpyPath2d(p) for p in PATH_2D])


def concat_paths_2d():
    base = Path2d()
    for p in PATH_2D:
        base.extend_multi_path(p)


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 3_000

print(f"Profiling NumpyPath2d and Path2d concatenation:")
print(
    f"Concatenate {len(PATH_2D)} paths to one multi-path."
)
profile(f"concat_np_paths() {RUNS}:", concat_np_paths, RUNS)
profile(f"concat_paths_2d() {RUNS}:", concat_paths_2d, RUNS)
profile(f"concat_2d_paths_to_np_path() {RUNS}:", concat_2d_paths_to_np_path, RUNS)

