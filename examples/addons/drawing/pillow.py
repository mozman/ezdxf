# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
import argparse
import sys
from time import perf_counter

import ezdxf
from ezdxf import recover, bbox
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pillow import PillowBackend


def main():
    parser = argparse.ArgumentParser(
        description="draw the given CAD file by Pillow and save it to a file"
    )
    parser.add_argument("cad_file", nargs="?")
    parser.add_argument("-o", "--out", required=True)
    parser.add_argument(
        "-x",
        "--width",
        type=int,
        default=1920,
        help="image width in pixels, default is 1920",
    )
    parser.add_argument(
        "-y",
        "--height",
        type=int,
        default=1080,
        help="image height in pixels, default is 1080",
    )
    args = parser.parse_args()

    if args.cad_file is None:
        print("no CAD file specified")
        sys.exit(1)

    try:
        doc = ezdxf.readfile(args.cad_file)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(2)
    except ezdxf.DXFError:
        try:
            doc, auditor = recover.readfile(args.cad_file)
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file: {args.cad_file}")
            sys.exit(3)
    else:
        auditor = doc.audit()

    if auditor.has_errors:
        # But is most likely good enough for rendering.
        print(f"Found {len(auditor.errors)} unrecoverable errors.")
    if auditor.has_fixes:
        print(f"Fixed {len(auditor.fixes)} errors.")

    try:
        layout = doc.modelspace()
    except KeyError:
        print(
            f'Could not find layout "{args.layout}". '
            f"Valid layouts: {[l.name for l in doc.layouts]}"
        )
        sys.exit(4)
    outfile = args.out

    # The current implementation is optimized to use as less memory as possible,
    # therefore the extents of the layout are required beforehand, otherwise the
    # backend would have to store all drawing commands to determine the required
    # image size.  This could be implemented as a different pillow backend which
    # is optimized for speed.
    print("detecting model space extents")
    t0 = perf_counter()
    extents = bbox.extents(layout, flatten=0)
    print(f"took {perf_counter()-t0:.1f}s {extents}")

    ctx = RenderContext(doc)
    out = PillowBackend(extents, image_size=(args.width, args.height))
    print("drawing model space")
    t0 = perf_counter()
    Frontend(ctx, out).draw_layout(layout)
    print(f"took {perf_counter() - t0:.1f}s")
    if outfile is not None:
        print(f'exporting to "{outfile}"')
        out.export(outfile)


if __name__ == "__main__":
    main()
