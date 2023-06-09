# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import time
import string
from ezdxf.fonts import fonts


def ttf_text_path():
    f = fonts.make_font("arial.ttf", 1)
    f.text_path(string.ascii_letters)


def shx_text_path():
    f = fonts.make_font("txt.shx", 1)
    f.text_path(string.ascii_letters)


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 3_000

print(f"Profiling text path creation:")
profile(f"ttf_text_path() {RUNS}x:", ttf_text_path, RUNS)
profile(f"shx_text_path() {RUNS}x:", shx_text_path, RUNS)

# 2023.06.09
# ttf_text_path() 3000x: 2.881s
# shx_text_path() 3000x: 1.161s
