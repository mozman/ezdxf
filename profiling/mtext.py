#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Callable
import time
from ezdxf.tools.text import fast_plain_mtext, plain_mtext, MTextParser

SHORT = "MTEXT short string"
LONG = (
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam "
    "nonumy eirmod tempor {\C1invidunt ut labore} et dolore mag{\C3na al}iquyam "
    "erat, sed {\C5diam voluptua.} At vero eos et accusam et justo duo dolores "
    "et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est "
    "Lorem ipsum dolor sit amet."
)

DEFAULT_COUNT = 10_000


def short_mtext_parser(count: int):
    for _ in range(count):
        list(MTextParser(SHORT))


def long_mtext_parser(count: int):
    for _ in range(count):
        list(MTextParser(LONG))


def short_fast_plain_mtext(count: int):
    for _ in range(count):
        fast_plain_mtext(SHORT)


def short_plain_mtext(count: int):
    for _ in range(count):
        plain_mtext(SHORT)


def long_fast_plain_mtext(count: int):
    for _ in range(count):
        fast_plain_mtext(LONG)


def long_plain_mtext(count: int):
    for _ in range(count):
        plain_mtext(LONG)


def print_result(count: int, t: float, text: str):
    print(f"{count}x {text} takes {t:.2f} s\n")


def run(func: Callable[[int], None], count: int = DEFAULT_COUNT):
    start = time.perf_counter()
    func(count)
    end = time.perf_counter()
    t = end - start
    print_result(count, t, func.__name__ + "()")
    return end - start


if __name__ == "__main__":
    run(short_mtext_parser)
    run(long_mtext_parser)
    run(short_fast_plain_mtext)
    run(short_plain_mtext)
    run(long_fast_plain_mtext)
    run(long_plain_mtext)
