# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import time
import numpy as np

numbers = [1, 2, 3, 4]


def convert_int8():
    _ = list(np.array(numbers, dtype=np.int8))


def value_from_int8():
    _ = np.array(numbers, dtype=np.int8)[1]


def convert_int16():
    _ = list(np.array(numbers, dtype=np.int16))


def value_from_int16():
    _ = np.array(numbers, dtype=np.int16)[1]


def convert_int32():
    _ = list(np.array(numbers, dtype=np.int32))


def value_from_int32():
    _ = np.array(numbers, dtype=np.int32)[1]


def convert_int64():
    _ = list(np.array(numbers, dtype=np.int64))


def value_from_int64():
    _ = np.array(numbers, dtype=np.int64)[1]


def profile(text, func, runs):
    t0 = time.perf_counter()
    for _ in range(runs):
        func()
    t1 = time.perf_counter()
    t = t1 - t0
    print(f"{text} {t:.3f}s")


RUNS = 1_000_000

print(f"Profiling numpy types:")
profile(f"convert_int8() {RUNS}:", convert_int8, RUNS)
profile(f"convert_int16() {RUNS}:", convert_int16, RUNS)
profile(f"convert_int32() {RUNS}:", convert_int32, RUNS)
profile(f"convert_int64() {RUNS}:", convert_int64, RUNS)

profile(f"value_from_int8() {RUNS}:", value_from_int8, RUNS)
profile(f"value_from_int16() {RUNS}:", value_from_int16, RUNS)
profile(f"value_from_int32() {RUNS}:", value_from_int32, RUNS)
profile(f"value_from_int64() {RUNS}:", value_from_int64, RUNS)
