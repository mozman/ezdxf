#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import os
import time
from ezdxf.lldxf.tagger import ascii_tags_loader, tag_compiler
from ezdxf.recover import safe_tag_loader
from ezdxf import EZDXF_TEST_FILES

BIG_FILE = os.path.join(EZDXF_TEST_FILES, "CADKitSamples", "torso_uniform.dxf")


def load_ascii():
    with open(BIG_FILE, "rt") as fp:
        list(tag_compiler(iter(ascii_tags_loader(fp))))


def safe_load_bytes():
    with open(BIG_FILE, "rb") as fp:
        list(safe_tag_loader(fp))


def print_result(time, text):
    print(f"Operation: {text} takes {time:.2f} s\n")


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == "__main__":
    print_result(run(safe_load_bytes), "safe_tag_loader()")
    print_result(run(load_ascii), "ascii_tag_compiler()")
