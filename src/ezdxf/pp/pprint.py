# Purpose: DXF Pretty Printer
# Copyright (c) 2015-2021, Manfred Moitzi
# License: MIT License
from typing import Iterable
import sys
import io
from pathlib import Path

from .dxfpp import dxfpp
from .rawpp import rawpp
from ezdxf.lldxf.const import DXFError, DXFStructureError
from ezdxf.lldxf.tagger import (
    ascii_tags_loader,
    tag_compiler,
    binary_tags_loader,
)
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.validator import is_dxf_file, is_binary_dxf_file
from ezdxf.filemanagement import dxf_file_info
from ezdxf.lldxf.repair import tag_reorder_layer
import webbrowser


def readfile(
    filename: str,
    legacy_mode: bool = False,
    compile_tags=True,
    is_binary_dxf=False,
) -> Iterable[DXFTag]:
    if is_binary_dxf:
        with open(filename, mode="rb") as fp:
            data = fp.read()
            tagger = binary_tags_loader(data)
    else:
        info = dxf_file_info(filename)
        fp = open(filename, mode="rt", encoding=info.encoding, errors="ignore")  # type: ignore
        tagger = ascii_tags_loader(fp)  # type: ignore

    if legacy_mode:
        tagger = tag_reorder_layer(tagger)
    if compile_tags:
        tagger = tag_compiler(iter(tagger))
    return tagger


def pretty_print(filename: Path, is_binary_dxf=False):
    try:
        tagger = readfile(
            str(filename), legacy_mode=True, is_binary_dxf=is_binary_dxf
        )
    except IOError:
        print(f'Unable to read DXF file "{filename}".')
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    html_filename = filename.parent / (filename.stem + ".html")
    try:
        with io.open(html_filename, mode="wt", encoding="utf-8") as fp:
            fp.write(dxfpp(tagger, filename.name))
    except IOError:
        print(f'IOError: can not write file "{html_filename}".')
    return html_filename


def raw_pretty_print(
    filename: Path, compile_tags=True, legacy_mode=False, is_binary_dxf=False
):
    try:
        tagger = readfile(
            str(filename),
            legacy_mode=legacy_mode,
            compile_tags=compile_tags,
            is_binary_dxf=is_binary_dxf,
        )
    except IOError:
        print(f'Unable to read DXF file "{filename}".')
        sys.exit(1)
    except DXFError as e:
        print(str(e))
        sys.exit(2)

    html_filename = filename.parent / (filename.stem + ".html")
    try:
        with io.open(html_filename, mode="wt", encoding="utf-8") as html:
            html.write(rawpp(tagger, str(filename), binary=is_binary_dxf))
    except IOError:
        print(f'IOError: can not write file "{filename}".')
    except DXFStructureError as e:
        print(f"DXFStructureError: {str(e)}")
    return html_filename


def run(args):
    for filename in args.files:
        if not Path(filename).exists():
            print(f'File "{filename}" not found.')
            continue

        if is_binary_dxf_file(filename):
            binary_dxf = True
        else:
            binary_dxf = False
            if not is_dxf_file(filename):
                print(f'File "{filename}" is not a DXF file.')
                continue

        if args.raw:
            html_path = raw_pretty_print(
                Path(filename),
                compile_tags=not args.nocompile,
                legacy_mode=args.legacy,
                is_binary_dxf=binary_dxf,
            )
        else:
            html_path = pretty_print(
                Path(filename), is_binary_dxf=binary_dxf
            )  # legacy mode is always used

        print(f'Created "{html_path}"')
        if args.open:
            webbrowser.open(str(html_path))
