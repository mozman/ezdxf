#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Callable, Optional, Dict, TYPE_CHECKING, Type
import abc
import sys
import os
import glob
import signal
import time
import logging
from pathlib import Path

import ezdxf
from ezdxf import recover
from ezdxf.lldxf import const
from ezdxf.lldxf.validator import is_dxf_file, is_binary_dxf_file
from ezdxf.dwginfo import dwg_file_info
from ezdxf import units

if TYPE_CHECKING:
    from ezdxf.entities import DXFGraphic
    from ezdxf.addons.drawing.properties import Properties

__all__ = ["get", "add_parsers"]

logger = logging.getLogger("ezdxf")


def get(cmd: str) -> Optional[Callable]:
    cls = _commands.get(cmd)
    if cls:
        return cls.run
    return None


def add_parsers(subparsers) -> None:
    for cmd in _commands.values():  # in order of registration
        cmd.add_parser(subparsers)


class Command:
    """abstract base class for launcher commands"""

    NAME = "command"

    @staticmethod
    @abc.abstractmethod
    def add_parser(subparsers) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def run(args) -> None:
        pass


_commands: Dict[str, Type[Command]] = dict()


def register(cls: Type[Command]):
    """Register a launcher sub-command."""
    _commands[cls.NAME] = cls
    return cls


@register
class PrettyPrint(Command):
    """Launcher sub-command: pp"""

    NAME = "pp"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            PrettyPrint.NAME, help="pretty print DXF files as HTML file"
        )
        parser.add_argument(
            "files",
            metavar="FILE",
            nargs="+",
            help="DXF files pretty print",
        )
        parser.add_argument(
            "-o",
            "--open",
            action="store_true",
            help="open generated HTML file by the default web browser",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            help="raw mode, no DXF structure interpretation",
        )
        parser.add_argument(
            "-x",
            "--nocompile",
            action="store_true",
            help="don't compile points coordinates into single tags "
            "(only in raw mode)",
        )
        parser.add_argument(
            "-l",
            "--legacy",
            action="store_true",
            help="legacy mode, reorder DXF point coordinates",
        )
        parser.add_argument(
            "-s",
            "--sections",
            action="store",
            default="hctbeo",
            help="choose sections to include and their order, h=HEADER, c=CLASSES, "
            "t=TABLES, b=BLOCKS, e=ENTITIES, o=OBJECTS",
        )

    @staticmethod
    def run(args):
        from ezdxf.pp import run

        run(args)


@register
class Audit(Command):
    """Launcher sub-command: audit"""

    NAME = "audit"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Audit.NAME, help="audit and repair DXF files"
        )
        parser.add_argument(
            "files",
            metavar="FILE",
            nargs="+",
            help="audit DXF files",
        )
        parser.add_argument(
            "-s",
            "--save",
            action="store_true",
            help='save recovered files with extension ".rec.dxf" ',
        )
        parser.add_argument(
            "-x",
            "--explore",
            action="store_true",
            help="filters invalid DXF tags, this may load corrupted files but "
            "data loss is very likely",
        )

    @staticmethod
    def run(args):
        def build_outname(name: str) -> str:
            p = Path(name)
            return str(p.parent / (p.stem + ".rec.dxf"))

        def log_fixes(auditor):
            for error in auditor.fixes:
                logger.info("fixed:" + error.message)

        def log_errors(auditor):
            for error in auditor.errors:
                logger.error(error.message)

        def _audit(filename: str) -> None:
            msg = f"auditing file: {filename}"
            print(msg)
            logger.info(msg)
            if args.explore:
                logger.info("explore mode - skipping invalid tags")
            loader = recover.explore if args.explore else recover.readfile
            try:
                doc, auditor = loader(filename)
            except IOError:
                msg = "Not a DXF file or a generic I/O error."
                print(msg)
                logger.error(msg)
                return  # keep on processing additional files
            except const.DXFStructureError as e:
                msg = f"Invalid or corrupted DXF file: {str(e)}"
                print(msg)
                logger.error(msg)
                return  # keep on processing additional files

            if auditor.has_errors:
                auditor.print_error_report()
                log_errors(auditor)
            if auditor.has_fixes:
                auditor.print_fixed_errors()
                log_fixes(auditor)

            if auditor.has_errors is False and auditor.has_fixes is False:
                print("No errors found.")
            else:
                print(
                    f"Found {len(auditor.errors)} errors, "
                    f"applied {len(auditor.fixes)} fixes"
                )

            if args.save:
                outname = build_outname(filename)
                doc.saveas(outname)
                print(f"Saved recovered file as: {outname}")

        for pattern in args.files:
            names = list(glob.glob(pattern))
            if len(names) == 0:
                msg = f"File(s) '{pattern}' not found."
                print(msg)
                logger.error(msg)
                continue
            for filename in names:
                if not os.path.exists(filename):
                    msg = f"File '{filename}' not found."
                    print(msg)
                    logger.error(msg)
                    continue
                if not is_dxf_file(filename):
                    msg = f"File '{filename}' is not a DXF file."
                    print(msg)
                    logger.error(msg)
                    continue
                _audit(filename)


def load_document(filename: str):
    try:
        doc, auditor = recover.readfile(filename)
    except IOError:
        msg = f'Not a DXF file or a generic I/O error: "{filename}"'
        print(msg, file=sys.stderr)
        sys.exit(2)
    except const.DXFStructureError:
        msg = f'Invalid or corrupted DXF file: "{filename}"'
        print(msg, file=sys.stderr)
        sys.exit(3)

    if auditor.has_errors:
        # But is most likely good enough for rendering.
        msg = (
            f"Audit process found {len(auditor.errors)} unrecoverable error(s)."
        )
        print(msg)
        logger.error(msg)
    if auditor.has_fixes:
        msg = f"Audit process fixed {len(auditor.fixes)} error(s)."
        print(msg)
        logger.info(msg)
    return doc, auditor


HELP_LTYPE = (
    "select the line type rendering method, default is approximate. "
    "Approximate uses the closest approximation available to the "
    "backend, the accurate method renders as accurately as possible "
    "but this approach is slower."
)
HELP_LWSCALE = (
    "set custom line weight scaling, default is 0 to disable line "
    "weights at all"
)


@register
class Draw(Command):
    """Launcher sub-command: draw"""

    NAME = "draw"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Draw.NAME, help="draw and convert DXF files by Matplotlib"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="?",
            help="DXF file to view or convert",
        )
        parser.add_argument(
            "--formats",
            action="store_true",
            help="show all supported export formats and exit",
        )
        parser.add_argument(
            "-l",
            "--layout",
            default="Model",
            help='select the layout to draw, default is "Model"',
        )
        parser.add_argument(
            "--all-layers-visible",
            action="store_true",
            help="draw all layers including the ones marked as invisible",
        )
        parser.add_argument(
            "--all-entities-visible",
            action="store_true",
            help="draw all entities including the ones marked as invisible "
            "(some entities are individually marked as invisible even "
            "if the layer is visible)",
        )
        parser.add_argument(
            "-o", "--out", required=False, help="output filename for export"
        )
        parser.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="target render resolution, default is 300",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="give more output",
        )

    @staticmethod
    def run(args):
        # Import on demand for a quicker startup:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Matplotlib package not found.")
            sys.exit(2)

        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        from ezdxf.addons.drawing.config import Configuration

        verbose = args.verbose
        # Print all supported export formats:
        if args.formats:
            fig = plt.figure()
            for (
                extension,
                description,
            ) in fig.canvas.get_supported_filetypes().items():
                print(f"{extension}: {description}")
            sys.exit(0)

        if args.file:
            filename = args.file
        else:
            print("argument FILE is required")
            sys.exit(1)
        print(f'loading file "{filename}"...')
        doc, _ = load_document(filename)

        try:
            layout = doc.layouts.get(args.layout)
        except KeyError:
            print(
                f'Could not find layout "{args.layout}". '
                f"Valid layouts: {[l.name for l in doc.layouts]}"
            )
            sys.exit(1)

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)

        if args.all_layers_visible:
            for layer_properties in ctx.layers.values():
                layer_properties.is_visible = True

        config = Configuration.defaults()
        if args.all_entities_visible:

            class AllVisibleFrontend(Frontend):
                def override_properties(
                    self, entity: "DXFGraphic", properties: "Properties"
                ) -> None:
                    properties.is_visible = True

            frontend = AllVisibleFrontend(ctx, out, config=config)
        else:
            frontend = Frontend(ctx, out, config=config)
        t0 = time.perf_counter()
        if verbose:
            print(f"drawing layout '{layout.name}' ...")
        frontend.draw_layout(layout, finalize=True)
        t1 = time.perf_counter()
        if verbose:
            print(f"took {t1-t0:.4f} seconds")
        if args.out is not None:
            print(f'exporting to "{args.out}"...')
            t0 = time.perf_counter()
            fig.savefig(args.out, dpi=args.dpi)
            plt.close(fig)
            t1 = time.perf_counter()
            if verbose:
                print(f"took {t1 - t0:.4f} seconds")

        else:
            if verbose:
                print("opening viewer...")
            plt.show()


@register
class View(Command):
    """Launcher sub-command: view"""

    NAME = "view"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            View.NAME, help="view DXF files by the PyQt viewer"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="?",
            help="DXF file to view",
        )
        parser.add_argument(
            "-l",
            "--layout",
            default="Model",
            help='select the layout to draw, default is "Model"',
        )
        # disable lineweight at all by default:
        parser.add_argument(
            "--lwscale",
            type=float,
            default=0,
            help=HELP_LWSCALE,
        )

    @staticmethod
    def run(args):
        # Import on demand for a quicker startup:
        try:
            from ezdxf.addons.xqt import QtWidgets
        except ImportError as e:
            print(str(e))
            sys.exit(1)
        from ezdxf.addons.drawing.qtviewer import CadViewer
        from ezdxf.addons.drawing.config import Configuration

        config = Configuration.defaults()
        config = config.with_changes(
            lineweight_scaling=args.lwscale,
        )

        signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
        app = QtWidgets.QApplication(sys.argv)
        set_app_icon(app)
        viewer = CadViewer(config=config)
        filename = args.file
        if filename:
            doc, auditor = load_document(filename)
            viewer.set_document(
                doc,
                auditor,
                layout=args.layout,
            )
        sys.exit(app.exec())


@register
class Pillow(Command):
    """Launcher sub-command: pil"""

    NAME = "pillow"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Pillow.NAME, help="draw and convert DXF files by Pillow"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="?",
            help="DXF file to draw",
        )
        parser.add_argument(
            "-o",
            "--out",
            required=False,
            help="output filename, the filename extension defines the image format "
            "(.png, .jpg, .tif, .bmp, ...)",
        )
        parser.add_argument(
            "-l",
            "--layout",
            type=str,
            default="Model",
            help='name of the layout to draw, default is "Model"',
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
            "-b",
            "--background",
            default=None,
            help='override background color in hex format "RRGGBB" or "RRGGBBAA", '
            'e.g. use "FFFFFF00" to get a white transparent background and a black '
            "foreground color (ACI=7), because a light background gets a "
            'black foreground color or vice versa  "00000000" for a black transparent '
            "background and a white foreground color.",
        ),
        parser.add_argument(
            "-r",
            "--oversampling",
            type=int,
            default=2,
            help="oversampling factor, default is 2, use 0 or 1 to disable oversampling",
        )
        parser.add_argument(
            "-m",
            "--margin",
            type=int,
            default=10,
            help="minimal margin around the image in pixels, default is 10",
        )
        parser.add_argument(
            "-t",
            "--text-mode",
            type=int,
            choices=[0, 1, 2, 3],
            default=2,
            help="text mode: 0=ignore, 1=placeholder, 2=outline, 3=filled, default is 2",
        )
        parser.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="output resolution in pixels/inch which is significant for the "
            "linewidth, default is 300",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="give more output",
        )

    @staticmethod
    def run(args):
        # Import on demand for a quicker startup:
        from ezdxf import bbox
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.config import Configuration, LinePolicy
        from ezdxf.addons.drawing.pillow import (
            PillowBackend,
            PillowBackendException,
        )
        from ezdxf.addons.drawing.properties import LayoutProperties

        verbose = args.verbose
        if args.file:
            filename = args.file
        else:
            print("argument FILE is required")
            sys.exit(1)
        print(f'loading file "{filename}"...')
        doc, _ = load_document(filename)
        try:
            layout = doc.layout(args.layout)
        except KeyError:
            print(f'layout "{args.layout}" not found')
            sys.exit(4)

        bg = args.background
        layout_properties = LayoutProperties.from_layout(layout)
        if bg is not None:
            if not bg.startswith("#"):
                bg = "#" + bg
            try:
                layout_properties.set_colors(bg)
            except ValueError:
                print(
                    f'ERROR: invalid background color value "{args.background}"'
                )
                sys.exit(4)

        ctx = RenderContext(doc)
        # force accurate linetype rendering by the frontend
        config = Configuration.defaults().with_changes(
            line_policy=LinePolicy.ACCURATE
        )
        if verbose:
            print(f"detecting extents...\n")
        bbox_cache = bbox.Cache()
        if layout.is_any_paperspace:
            # get entity bounding boxes in modelspace for faster paperspace
            # rendering
            bbox.extents(doc.modelspace(), fast=True, cache=bbox_cache)
        extents = bbox.extents(layout, fast=True, cache=bbox_cache)
        img_x, img_y = parse_image_size(args.image_size)
        if verbose:
            print(f"    units: {units.unit_name(layout.units)}")
            print(
                f"    modelspace size: {extents.size.x:.3f} x {extents.size.y:.3f}"
            )
            print(
                f"    min extents: ({extents.extmin.x:.3f}, {extents.extmin.y:.3f})"
            )
            print(
                f"    max extents: ({extents.extmax.x:.3f}, {extents.extmax.y:.3f})"
            )
            print(f"\nimage size: {img_x} x {img_y}")
        try:
            out = PillowBackend(
                extents,
                image_size=(img_x, img_y),
                oversampling=args.oversampling,
                margin=args.margin,
                dpi=args.dpi,
                text_mode=args.text_mode,
            )
        except PillowBackendException as e:
            print(str(e))
            sys.exit(5)

        t0 = time.perf_counter()
        if verbose:
            print(f'drawing layout "{layout.name}"...')
        Frontend(ctx, out, config=config, bbox_cache=bbox_cache).draw_layout(
            layout, layout_properties=layout_properties
        )
        t1 = time.perf_counter()
        if verbose:
            print(f"took {t1-t0:.4f} seconds")
        if args.out is not None:
            print(f'exporting to "{args.out}"')
            t0 = time.perf_counter()
            out.export(args.out)
            t1 = time.perf_counter()
            if verbose:
                print(f"took {t1 - t0:.4f} seconds")
        else:
            if verbose:
                print("opening image with the default system viewer...")
            out.resize().show(args.file)


def parse_image_size(image_size: str) -> tuple[int, int]:
    if "," in image_size:
        sx, sy = image_size.split(",")
    elif "x" in image_size:
        sx, sy = image_size.split("x")
    else:
        sx = int(image_size)  # type: ignore
        sy = sx
    return int(sx), int(sy)


@register
class Browse(Command):
    """Launcher sub-command: browse"""

    NAME = "browse"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Browse.NAME, help="browse DXF file structure"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="?",
            help="DXF file to browse",
        )
        parser.add_argument(
            "-l", "--line", type=int, required=False, help="go to line number"
        )
        parser.add_argument(
            "-g",
            "--handle",
            required=False,
            help="go to entity by HANDLE, HANDLE has to be a hex value without "
            "any prefix like 'fefe'",
        )

    @staticmethod
    def run(args):
        try:
            from ezdxf.addons.xqt import QtWidgets
        except ImportError as e:
            print(str(e))
            sys.exit(1)
        from ezdxf.addons import browser

        signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
        app = QtWidgets.QApplication(sys.argv)
        set_app_icon(app)
        main_window = browser.DXFStructureBrowser(
            args.file,
            line=args.line,
            handle=args.handle,
            resource_path=resources_path(),
        )
        main_window.show()
        sys.exit(app.exec())


@register
class BrowseAcisData(Command):
    """Launcher sub-command: browse-acis"""

    NAME = "browse-acis"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            BrowseAcisData.NAME, help="browse ACIS structures in DXF files"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="?",
            help="DXF file to browse",
        )
        parser.add_argument(
            "-g",
            "--handle",
            required=False,
            help="go to entity by HANDLE, HANDLE has to be a hex value without "
            "any prefix like 'fefe'",
        )

    @staticmethod
    def run(args):
        try:
            from ezdxf.addons.xqt import QtWidgets
        except ImportError as e:
            print(str(e))
            sys.exit(1)
        from ezdxf.addons.acisbrowser.browser import AcisStructureBrowser

        signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
        app = QtWidgets.QApplication(sys.argv)
        set_app_icon(app)
        main_window = AcisStructureBrowser(
            args.file,
            handle=args.handle,
        )
        main_window.show()
        sys.exit(app.exec())


@register
class Strip(Command):
    """Launcher sub-command: strip"""

    NAME = "strip"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Strip.NAME, help="strip comments from DXF files"
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="+",
            help='DXF file to process, wildcards "*" and "?" are supported',
        )
        parser.add_argument(
            "-b",
            "--backup",
            action="store_true",
            required=False,
            help='make a backup copy with extension ".bak" from the '
            "DXF file, overwrites existing backup files",
        )
        parser.add_argument(
            "-t",
            "--thumbnail",
            action="store_true",
            required=False,
            help="strip THUMBNAILIMAGE section",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            required=False,
            help="give more output",
        )

    @staticmethod
    def run(args):
        from ezdxf.tools.strip import strip

        for pattern in args.file:
            for filename in glob.glob(pattern):
                strip(
                    filename,
                    backup=args.backup,
                    thumbnail=args.thumbnail,
                    verbose=args.verbose,
                )


@register
class Config(Command):
    """Launcher sub-command: config"""

    NAME = "config"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(Config.NAME, help="manage config files")
        parser.add_argument(
            "-p",
            "--print",
            action="store_true",
            help="print configuration",
        )
        parser.add_argument(
            "-w",
            "--write",
            metavar="FILE",
            help="write configuration",
        )
        parser.add_argument(
            "--home",
            action="store_true",
            help="create config file 'ezdxf.ini' in the user home directory "
            "'~/.config/ezdxf', $XDG_CONFIG_HOME is supported if set",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="factory reset, delete default config files 'ezdxf.ini'",
        )

    @staticmethod
    def run(args):
        from ezdxf import options

        if args.reset:
            options.reset()
            options.delete_default_config_files()
        if args.home:
            options.write_home_config()
        if args.print:
            options.print()
        if args.write:
            filepath = Path(args.write).expanduser()
            try:
                options.write_file(str(filepath))
                print(f"configuration written to: {filepath}")
            except IOError as e:
                print(str(e))


def load_every_document(filename: str):
    def io_error() -> str:
        msg = f'Not a DXF file or a generic I/O error: "{filename}"'
        print(msg, file=sys.stderr)
        return msg

    def structure_error() -> str:
        msg = f'Invalid or corrupted DXF file: "{filename}"'
        print(msg, file=sys.stderr)
        return msg

    binary_fmt = False
    if is_binary_dxf_file(filename):
        try:
            doc = ezdxf.readfile(filename)
        except IOError:
            raise const.DXFLoadError(io_error())
        except const.DXFStructureError:
            raise const.DXFLoadError(structure_error())
        auditor = doc.audit()
        binary_fmt = True
    else:
        try:
            doc, auditor = recover.readfile(filename)
        except IOError:
            raise const.DXFLoadError(io_error())
        except const.DXFStructureError:
            dwginfo = dwg_file_info(filename)
            if dwginfo.version != "invalid":
                print(
                    f"This is a DWG file!!!\n"
                    f'Filename: "{filename}"\n'
                    f"Format: DWG\n"
                    f"Release: {dwginfo.release}\n"
                    f"DWG Version: {dwginfo.version}\n"
                )
                raise const.DXFLoadError()
            raise const.DXFLoadError(structure_error())
    return doc, auditor, binary_fmt


@register
class Info(Command):
    """Launcher sub-command: info"""

    NAME = "info"

    @staticmethod
    def add_parser(subparsers):
        parser = subparsers.add_parser(
            Info.NAME,
            help="show information and optional stats of DXF files as "
            "loaded by ezdxf, this may not represent the original "
            "content of the file, use the browse command to "
            "see the original content",
        )
        parser.add_argument(
            "file",
            metavar="FILE",
            nargs="+",
            help='DXF file to process, wildcards "*" and "?" are supported',
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            required=False,
            help="give more output",
        )
        parser.add_argument(
            "-s",
            "--stats",
            action="store_true",
            required=False,
            help="show content stats",
        )

    @staticmethod
    def run(args):
        from ezdxf.document import info

        def process(fn: str):
            try:
                doc, auditor, binary_fmt = load_every_document(fn)
            except const.DXFLoadError:
                pass
            else:
                fmt = "Binary" if binary_fmt else "ASCII"
                print(
                    "\n".join(
                        info(
                            doc,
                            verbose=args.verbose,
                            content=args.stats,
                            fmt=fmt,
                        )
                    )
                )
                if auditor.has_fixes:
                    print(f"Audit process fixed {len(auditor.fixes)} error(s).")
                if auditor.has_errors:
                    print(
                        f"Audit process found {len(auditor.errors)} unrecoverable error(s)."
                    )
                print()

        for pattern in args.file:
            file_count = 0
            for filename in glob.glob(pattern):
                if os.path.isdir(filename):
                    dir_pattern = os.path.join(filename, "*.dxf")
                    for filename2 in glob.glob(dir_pattern):
                        process(filename2)
                        file_count += 1
                else:
                    process(filename)
                    file_count += 1

            if file_count == 0:
                sys.stderr.write(
                    f'No matching files for pattern: "{pattern}"\n'
                )


def set_app_icon(app):
    from ezdxf.addons.xqt import QtGui, QtCore

    app_icon = QtGui.QIcon()
    p = resources_path()
    app_icon.addFile(str(p / "16x16.png"), QtCore.QSize(16, 16))
    app_icon.addFile(str(p / "24x24.png"), QtCore.QSize(24, 24))
    app_icon.addFile(str(p / "32x32.png"), QtCore.QSize(32, 32))
    app_icon.addFile(str(p / "48x48.png"), QtCore.QSize(48, 48))
    app_icon.addFile(str(p / "64x64.png"), QtCore.QSize(64, 64))
    app_icon.addFile(str(p / "256x256.png"), QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)


def resources_path():
    from pathlib import Path

    return Path(__file__).parent / "resources"
