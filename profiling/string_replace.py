# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import time
from ezdxf.tools.text_layout import lorem_ipsum
import re

REPLACE = {"Lorem": "", "ipsum": "", "dolor": "", "sit": ""}


def re_replace(rep, text):
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


def str_replace(rep, text):
    for old, new in rep.items():
        text = text.replace(old, new)


def find_substr(rep, text):
    for old, new in rep.items():
        text.find(old)


def contains_substr(rep, text):
    for old, new in rep.items():
        result = old in text


def profile(text, func, runs):
    content = " ".join(lorem_ipsum(1000))
    t0 = time.perf_counter()
    for _ in range(runs):
        func(REPLACE, content)
    t1 = time.perf_counter()
    t = t1 - t0
    print(f'{text} {t:.3f}s')


RUNS = 1_000

print(f'Profiling text replacement:')
profile(f'str_replace() {RUNS}:', str_replace, RUNS)
profile(f're_replace() {RUNS}:', re_replace, RUNS)
profile(f'find_substr() {RUNS * 100}:', find_substr, RUNS * 100)
profile(f'contains_substr() {RUNS * 100}:', contains_substr, RUNS * 100)
