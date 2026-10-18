"""Synthetic benchmark; run against baseline/candidate via PYTHONPATH."""

import argparse
import gc
import json
import platform
import statistics
import time
from pathlib import Path
import ezdxf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    from ezdxf import bbox

    doc = ezdxf.new()
    msp = doc.modelspace()
    lines = [
        msp.add_line((i % 200, i // 200), (i % 200 + 0.8, i // 200 + 0.5))
        for i in range(20_000)
    ]

    def operation():
        return bbox.extents(lines)

    assert operation().has_data
    operation()  # warm-up
    samples = []
    for _ in range(args.repeat):
        gc.collect()
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000)
    result = {
        "workload": "20,000 LINE bounds; no bbox cache",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "source": ezdxf.__file__,
        "native_extensions": ezdxf.options.use_c_ext,
        "median_ms": statistics.median(samples),
        "samples_ms": samples,
    }
    text = json.dumps(result, indent=2) + "\n"
    print(text, end="")
    if args.output:
        args.output.write_text(text)


if __name__ == "__main__":
    main()
