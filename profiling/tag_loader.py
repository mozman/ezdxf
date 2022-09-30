#  Copyright (c) 2020-2022, Manfred Moitzi
#  License: MIT License
import time
import ezdxf
from ezdxf.lldxf.tagger import ascii_tags_loader
from ezdxf.recover import bytes_loader, synced_bytes_loader

BIG_FILE = ezdxf.options.test_files_path / "CADKitSamples" / "torso_uniform.dxf"


def load_ascii():
    with open(BIG_FILE, "rt") as fp:
        list(ascii_tags_loader(fp))


def load_bytes():
    with open(BIG_FILE, "rb") as fp:
        list(bytes_loader(fp))


def load_synced_bytes():
    with open(BIG_FILE, "rb") as fp:
        list(synced_bytes_loader(fp))


def print_result(time, text):
    print(f"Operation: {text} takes {time:.2f} s\n")


def run(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


if __name__ == "__main__":
    print_result(run(load_ascii), "ascii_tags_loader()")
    print_result(run(load_bytes), "bytes_loader()")
    print_result(run(load_synced_bytes), "synced_bytes_loader()")
