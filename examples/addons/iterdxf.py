# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
import time
import pathlib
import ezdxf
from ezdxf.addons import iterdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how iterate over very big DXF files without loading them
# into memory. This takes much longer, but it's maybe the only way to process
# these very large files.
# ------------------------------------------------------------------------------


def main():
    t0 = time.perf_counter()
    doc = iterdxf.opendxf(ezdxf.options.test_files_path / "GKB-R2010.dxf")
    line_exporter = doc.export(CWD / "lines.dxf")
    text_exporter = doc.export(CWD / "text.dxf")
    polyline_exporter = doc.export(CWD / "polyline.dxf")
    lwpolyline_exporter = doc.export(CWD / "lwpolyline.dxf")
    try:
        for entity in doc.modelspace():
            if entity.dxftype() == "LINE":
                line_exporter.write(entity)
            elif entity.dxftype() == "TEXT":
                text_exporter.write(entity)
            elif entity.dxftype() == "POLYLINE":
                polyline_exporter.write(entity)
            elif entity.dxftype() == "LWPOLYLINE":
                lwpolyline_exporter.write(entity)
    finally:
        line_exporter.close()
        text_exporter.close()
        polyline_exporter.close()
        lwpolyline_exporter.close()
        doc.close()

    print(f"Processing time: {time.perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    main()
