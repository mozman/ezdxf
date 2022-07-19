# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from typing import Tuple
import argparse
import sys
from time import perf_counter

import ezdxf
from ezdxf import recover, bbox
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pillow import PillowBackend, PillowDelayedDraw

DIRECT_DRAW = True


def main():
    parser = argparse.ArgumentParser(
        description='draw the given CAD file by the "Pillow" package and export '
        "it as a pixel based image file"
    )
    parser.add_argument("cad_file", nargs="?")
    parser.add_argument(
        "-o",
        "--out",
        required=True,
        help="output filename, the filename extension defines the image format "
        "(.png, .jpg, .tif, .bmp, ...)",
    )
    parser.add_argument(
        "-i",
        "--image_size",
        type=str,
        default="1920,1080",
        help='image size in pixels as "width,height", default is "1920,1080", '
        'supports also "x" as delimiter like "1920x1080". A single integer '
        'is used for both directions e.g. "2000" defines an image size of '
        "2000x2000. The image is centered for the smaller DXF drawing extent.",
    )
    parser.add_argument(
        "-r",
        "--oversampling",
        type=int,
        default=2,
        help="oversampling factor, default is 2, use 0 or 1 to disable oversampling",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="output resolution in pixels/inch, default is 300",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="use fast bounding box calculation",
    )
    parser.add_argument(
        "-t",
        "--text-placeholder",
        action="store_true",
        help="draw rectangle as text placeholder",
    )
    parser.add_argument(
        "-d",
        "--delayed",
        action="store_true",
        help="delayed draw",
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

    msp = doc.modelspace()
    outfile = args.out
    img_x, img_y = parse_image_size(args.image_size)
    print(f"Image size: {img_x}x{img_y}")
    print(f"DPI: {args.dpi}")
    print(f"Oversampling factor: {args.oversampling}")
    print(f"Draw text placeholder: {args.text_placeholder}")
    # The current implementation is optimized to use as less memory as possible,
    # therefore the extents of the layout are required beforehand, otherwise the
    # backend would have to store all drawing commands to determine the required
    # image size.  This could be implemented as a different pillow backend which
    # is optimized for speed.
    ctx = RenderContext(doc)
    try:
        if args.delayed:
            out = PillowDelayedDraw(
                image_size=(img_x, img_y),
                oversampling=args.oversampling,
                dpi=args.dpi,
                text_placeholder=args.text_placeholder,
            )
        else:
            print(f"detecting model space extents (fast={args.fast}) ...")
            t0 = perf_counter()
            extents = bbox.extents(msp, fast=args.fast)
            print(f"... in {perf_counter() - t0:.1f}s")
            print(f"EXTMIN: ({extents.extmin.x:.3f}, {extents.extmin.y:.3f})")
            print(f"EXTMAX: ({extents.extmax.x:.3f}, {extents.extmax.y:.3f})")
            print(f"SIZE: ({extents.size.x:.3f}, {extents.size.y:.3f})")
            out = PillowBackend(
                extents,
                image_size=(img_x, img_y),
                oversampling=args.oversampling,
                dpi=args.dpi,
                text_placeholder=args.text_placeholder,
            )
    except ValueError as e:
        # invalid image size or empty drawing
        print(str(e))
        sys.exit(1)

    print("drawing model space ...")
    t0 = perf_counter()
    Frontend(ctx, out).draw_layout(msp)
    print(f"... in {perf_counter() - t0:.1f}s")
    if outfile is not None:
        t0 = perf_counter()
        out.export(outfile)
        print(f'exported image to "{outfile}" in {perf_counter() - t0:.1f}s')


def parse_image_size(image_size: str) -> Tuple[int, int]:
    if "," in image_size:
        sx, sy = image_size.split(",")
    elif "x" in image_size:
        sx, sy = image_size.split("x")
    else:
        sx = int(image_size)
        sy = sx
    return int(sx), int(sy)


if __name__ == "__main__":
    main()
