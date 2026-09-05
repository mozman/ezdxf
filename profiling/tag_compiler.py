#  Copyright (c) 2020-2026, Manfred Moitzi
#  License: MIT License
import time
import ezdxf
from ezdxf.lldxf.tagger import (
    ascii_tags_loader,
    tag_compiler,
    ascii_tag_compiler,
)
from ezdxf.recover import safe_tag_loader

BIG_FILE = ezdxf.options.test_files_path / "CADKitSamples" / "torso_uniform.dxf"


def load_ascii():
    with open(BIG_FILE, "rt") as fp:
        list(tag_compiler(iter(ascii_tags_loader(fp))))


def load_fused_ascii():
    with open(BIG_FILE, "rt") as fp:
        list(ascii_tag_compiler(fp))


def safe_load_bytes():
    with open(BIG_FILE, "rb") as fp:
        list(safe_tag_loader(fp))


def read_document():
    with open(BIG_FILE, "rt") as fp:
        ezdxf.read(fp)


def print_result(time, text):
    print(f"Operation: {text} takes {time:.2f} s\n")


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == "__main__":
    print_result(run(safe_load_bytes), "safe_tag_loader()")
    print_result(run(load_ascii), "tag_compiler(ascii_tags_loader())")
    print_result(run(load_fused_ascii), "ascii_tag_compiler()")
    print_result(run(read_document), "ezdxf.read()")
