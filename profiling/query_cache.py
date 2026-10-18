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
    from ezdxf.query import EntityQuery

    doc = ezdxf.new()
    msp = doc.modelspace()
    lines = [
        msp.add_line((i, 0), (i + 1, 0), dxfattribs={"layer": "A" if i % 2 else "B"})
        for i in range(100)
    ]
    expression = 'LINE[layer=="A" & color==256]'

    def operation():
        return [EntityQuery(lines, expression) for _ in range(100)]

    assert len(operation()[0]) == 50
    operation()  # warm-up
    samples = []
    for _ in range(args.repeat):
        gc.collect()
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000)
    result = {
        "workload": "100 repeated queries over 100 LINE entities",
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
