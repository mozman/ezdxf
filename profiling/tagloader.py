# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from ezdxf.acc import USE_C_EXT

if USE_C_EXT is False:
    print('C-extension disabled or not available.')
    sys.exit(1)

import ezdxf

from ezdxf.lldxf import tagger
from ezdxf.acc import tagger as ctagger
from ezdxf.version import __version__


def open_log(name: str):
    parent = Path(__file__).parent
    p = parent / 'logs' / Path(name + '.csv')
    if not p.exists():
        with open(p, mode='wt') as fp:
            fp.write(
                '"timestamp"; "pytime"; "cytime"; '
                '"python_version"; "ezdxf_version"\n')
    log_file = open(p, mode='at')
    return log_file


def log(name: str, pytime: float, cytime: float):
    log_file = open_log(name)
    timestamp = datetime.now().isoformat()
    log_file.write(
        f'{timestamp}; {pytime}; {cytime}; "{sys.version}"; "{__version__}"\n')
    log_file.close()


def py_compiler(fp):
    loader = tagger.ascii_tags_loader(fp)
    list(tagger.tag_compiler(loader))


def cy_compiler(fp):
    loader = ctagger.ascii_tags_loader(fp)
    list(ctagger.tag_compiler(loader))


def tags_loader(loader, fname):
    with open(fname, 'rt') as fp:
        list(loader(fp))


def tags_compiler(compiler, fname):
    with open(fname, 'rt') as fp:
        compiler(fp)


def profile1(func, *args) -> float:
    t0 = time.perf_counter()
    func(*args)
    t1 = time.perf_counter()
    return t1 - t0


def profile(text, func, pytype, cytype, *args):
    pytime = profile1(func, pytype, *args)
    cytime = profile1(func, cytype, *args)
    ratio = pytime / cytime
    print(f'Python - {text} {pytime:.3f}s')
    print(f'Cython - {text} {cytime:.3f}s')
    print(f'Ratio {ratio:.1f}x')
    log(func.__name__, pytime, cytime)


FILE = os.path.join(
    ezdxf.EZDXF_TEST_FILES, "CADKitSamples",
    "AEC Plan Elev Sample.dxf")

print(f'filling file cache ...')
tags_loader(ctagger.ascii_tags_loader, FILE)

print(f'Profiling loading functions as Python and Cython implementation:')
profile(f'loading tags from "{FILE}": ', tags_loader,
        tagger.ascii_tags_loader, ctagger.ascii_tags_loader, FILE)
profile(f'compile tags from "{FILE}": ', tags_compiler,
        py_compiler, cy_compiler, FILE)
