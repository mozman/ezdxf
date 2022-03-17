# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License
# type: ignore
import logging
import os
import platform
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Union

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.validator import (
    is_dxf_file,
    dxf_info,
    is_binary_dxf_file,
    dwg_version,
)

logger = logging.getLogger("ezdxf")
win_exec_path = ezdxf.options.get("odafc-addon", "win_exec_path").strip('"')


class ODAFCError(IOError):
    pass


class UnknownODAFCError(ODAFCError):
    pass


class ODAFCNotInstalledError(ODAFCError):
    pass


class UnsupportedFileFormat(ODAFCError):
    pass


class UnsupportedPlatform(ODAFCError):
    pass


class UnsupportedVersion(ODAFCError):
    pass


VERSION_MAP = {
    "R12": "ACAD12",
    "R13": "ACAD13",
    "R14": "ACAD14",
    "R2000": "ACAD2000",
    "R2004": "ACAD2004",
    "R2007": "ACAD2007",
    "R2010": "ACAD2010",
    "R2013": "ACAD2013",
    "R2018": "ACAD2018",
    "AC1004": "ACAD9",
    "AC1006": "ACAD10",
    "AC1009": "ACAD12",
    "AC1012": "ACAD13",
    "AC1014": "ACAD14",
    "AC1015": "ACAD2000",
    "AC1018": "ACAD2004",
    "AC1021": "ACAD2007",
    "AC1024": "ACAD2010",
    "AC1027": "ACAD2013",
    "AC1032": "ACAD2018",
}

VALID_VERSIONS = {
    "ACAD9",
    "ACAD10",
    "ACAD12",
    "ACAD13",
    "ACAD14",
    "ACAD2000",
    "ACAD2004",
    "ACAD2007",
    "ACAD2010",
    "ACAD2013",
    "ACAD2018",
}


def is_installed() -> bool:
    """Returns ``True`` if the ODAFileConverter is installed.

    .. versionadded:: 0.18

    """
    if platform.system() in ("Linux", "Darwin"):
        return shutil.which("ODAFileConverter") is not None
    # Windows:
    return os.path.exists(win_exec_path)


def map_version(version: str) -> str:
    return VERSION_MAP.get(version.upper(), version.upper())


def readfile(
    filename: str, version: Optional[str] = None, *, audit: bool = False
) -> Optional[Drawing]:
    """Use an installed `ODA File Converter`_ to convert a DWG/DXB/DXF file
    into a temporary DXF file and load this file by `ezdxf`.

    Args:
        filename: file to load by ODA File Converter
        version: load file as specific DXF version, by default the same version
            as the source file or if not detectable the latest by `ezdxf`
            supported version.
        audit: audit source file before loading

    Raises:
        FileNotFoundError: source file not found
        odafc.UnknownODAFCError: conversion failed for unknown reasons
        odafc.UnsupportedVersion: invalid DWG version specified
        odafc.UnsupportedFileFormat: unsupported file extension
        odafc.ODAFCNotInstalledError: ODA File Converter not installed

    """
    infile = Path(filename).absolute()
    if not infile.is_file():
        raise FileNotFoundError(f"No such file: '{infile}'")
    version = _detect_version(filename) if version is None else version

    with tempfile.TemporaryDirectory(prefix="odafc_") as tmp_dir:
        args = _odafc_arguments(
            infile.name,
            str(infile.parent),
            tmp_dir,
            output_format="DXF",
            version=version,
            audit=audit,
        )
        _execute_odafc(args)
        out_file = Path(tmp_dir) / infile.with_suffix(".dxf").name
        if out_file.exists():
            doc = ezdxf.readfile(str(out_file))
            doc.filename = infile.with_suffix(".dxf")
            return doc
    raise UnknownODAFCError("Failed to convert file: Unknown Error")


def export_dwg(
    doc: Drawing,
    filename: str,
    version: Optional[str] = None,
    *,
    audit: bool = False,
    replace: bool = False,
) -> None:
    """Use an installed `ODA File Converter`_ to export a DXF document `doc`
    as a DWG file.

    Saves a temporary DXF file and convert this DXF file into a DWG file by the
    ODA File Converter. If `version` is not specified the DXF version of the
    source document is used.

    Args:
        doc: `ezdxf` DXF document as :class:`~ezdxf.drawing.Drawing` object
        filename: export filename of DWG file, extension will be changed to ".dwg"
        version: export file as specific version, by default the same version as
            the source document.
        audit: audit source file by ODA File Converter at exporting
        replace: replace existing DWG file if ``True``

    Raises:
        FileExistsError: target file already exists, and argument `replace` is
            ``False``
        FileNotFoundError: parent directory of target file does not exist
        odafc.UnknownODAFCError: exporting DWG failed for unknown reasons
        odafc.ODAFCNotInstalledError: ODA File Converter not installed

    """
    if version is None:
        version = doc.dxfversion
    export_version = VERSION_MAP[version]
    dwg_file = Path(filename).absolute()
    out_folder = Path(dwg_file.parent)
    if dwg_file.exists():
        if replace:
            dwg_file.unlink()
        else:
            raise FileExistsError(f"File already exists: {dwg_file}")
    if out_folder.exists():
        with tempfile.TemporaryDirectory(prefix="odafc_") as tmp_dir:
            dxf_file = Path(tmp_dir) / dwg_file.with_suffix(".dxf").name

            # Save DXF document
            old_filename = doc.filename
            doc.saveas(dxf_file)
            doc.filename = old_filename

            arguments = _odafc_arguments(
                dxf_file.name,
                tmp_dir,
                str(out_folder),
                output_format="DWG",
                version=export_version,
                audit=audit,
            )
            _execute_odafc(arguments)
    else:
        raise FileNotFoundError(
            f"No such file or directory: '{str(out_folder)}'"
        )


def convert(
    source: Union[str, Path],
    dest: Union[str, Path] = "",
    *,
    version="R2018",
    audit=True,
    replace=False,
):
    """Convert `source` file to `dest` file.

    .. versionadded::  0.18

    The file extension defines the target format
    e.g. :code:`convert("test.dxf", "Test.dwg")` converts the source file to a
    DWG file.
    If `dest` is an empty string the conversion depends on the source file
    format and is DXF to DWG or DWG to DXF.
    To convert DXF to DXF an explicit destination filename is required:
    :code:`convert("r12.dxf", "r2013.dxf", version="R2013")`

    Args:
        source: source file
        dest: destination file, an empty string uses the source filename with
            the extension of the target format e.g. "test.dxf" -> "test.dwg"
        version: output DXF/DWG version e.g. "ACAD2018", "R2018", "AC1032"
        audit: audit files
        replace: replace existing destination file

    Raises:
        FileNotFoundError: source file or destination folder does not exist
        FileExistsError: destination file already exists and argument `replace`
            is ``False``
        odafc.UnsupportedVersion: invalid DXF version specified
        odafc.UnsupportedFileFormat: unsupported file extension
        odafc.UnknownODAFCError: conversion failed for unknown reasons
        odafc.ODAFCNotInstalledError: ODA File Converter not installed

    """
    version = map_version(version)
    if version not in VALID_VERSIONS:
        raise UnsupportedVersion(f"Invalid version: '{version}'")
    src_path = Path(source).expanduser().absolute()
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: '{source}'")
    if dest:
        dest_path = Path(dest)
    else:
        ext = src_path.suffix.lower()
        if ext == ".dwg":
            dest_path = src_path.with_suffix(".dxf")
        elif ext == ".dxf":
            dest_path = src_path.with_suffix(".dwg")
        else:
            raise UnsupportedFileFormat(f"Unsupported file format: '{ext}'")
    if dest_path.exists() and not replace:
        raise FileExistsError(f"Target file already exists: '{dest_path}'")
    if not dest_path.parent.is_dir():
        # Cannot copy result to destination folder!
        FileNotFoundError(
            f"Destination folder does not exist: '{dest_path.parent}'"
        )
    ext = dest_path.suffix
    fmt = ext.upper()[1:]
    if fmt not in ("DXF", "DWG"):
        raise UnsupportedFileFormat(f"Unsupported file format: '{ext}'")

    with tempfile.TemporaryDirectory(prefix="odafc_") as tmp_dir:
        arguments = _odafc_arguments(
            src_path.name,
            in_folder=str(src_path.parent),
            out_folder=str(tmp_dir),
            output_format=fmt,
            version=version,
            audit=audit,
        )
        _execute_odafc(arguments)
        result = list(Path(tmp_dir).iterdir())
        if result:
            try:
                shutil.move(result[0], dest_path)
            except IOError:
                shutil.copy(result[0], dest_path)
        else:
            UnknownODAFCError(f"Unknown error: no {fmt} file was created")


def _detect_version(path: str) -> str:
    """Returns the DXF/DWG version of file `path` as ODAFC compatible version
    string.

    Raises:
        odafc.UnsupportedVersion: unknown or unsupported DWG version
        odafc.UnsupportedFileFormat; unsupported file extension

    """
    version = "ACAD2018"
    ext = os.path.splitext(path)[1].lower()
    if ext == ".dxf":
        if is_binary_dxf_file(path):
            pass
        elif is_dxf_file(path):
            with open(path, "rt") as fp:
                info = dxf_info(fp)
                version = VERSION_MAP[info.version]
    elif ext == ".dwg":
        version = dwg_version(path)
        if version is None:
            raise UnsupportedVersion("Unknown or unsupported DWG version.")
    else:
        raise UnsupportedFileFormat(f"Unsupported file format: '{ext}'")

    return map_version(version)


def _odafc_arguments(
    filename: str,
    in_folder: str,
    out_folder: str,
    output_format: str = "DXF",
    version: str = "ACAD2013",
    audit: bool = False,
) -> List[str]:
    """ODA File Converter command line format:

    ODAFileConverter "Input Folder" "Output Folder" version type recurse audit [filter]

        - version: output version: "ACAD9" - "ACAD2018"
        - type: output file type: "DWG", "DXF", "DXB"
        - recurse: recurse Input Folder: "0" or "1"
        - audit: audit each file: "0" or "1"
        - optional Input files filter: default "*.DWG,*.DXF"

    """
    recurse = "0"
    audit_str = "1" if audit else "0"
    return [
        in_folder,
        out_folder,
        version,
        output_format,
        recurse,
        audit_str,
        filename,
    ]


def _get_odafc_path(system: str) -> str:
    """Get ODAFC application path.

    Raises:
        odafc.ODAFCNotInstalledError: ODA File Converter not installed

    """
    path = shutil.which("ODAFileConverter")
    if not path and system == "Windows":
        path = win_exec_path
        if not Path(path).is_file():
            path = None

    if not path:
        raise ODAFCNotInstalledError(
            f"Could not find ODAFileConverter in the path. "
            f"Install application from https://www.opendesign.com/guestfiles/oda_file_converter"
        )
    return path


@contextmanager
def _linux_dummy_display():
    """See xvbfwrapper library for a more feature complete xvfb interface."""
    if shutil.which("Xvfb"):
        display = ":123"  # arbitrary choice
        proc = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", "800x600x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.1)
        yield display
        try:
            proc.terminate()
            proc.wait()
        except OSError:
            pass
    else:
        logger.warning(
            f"Install xvfb to prevent the ODAFileConverter GUI from opening"
        )
        yield os.environ["DISPLAY"]


def _run_with_no_gui(
    system: str, command: str, arguments: List[str]
) -> subprocess.Popen:
    """Execute ODAFC application without launching the GUI.

    Args:
        system: "Linux", "Windows" or "Darwin"
        command: application to execute
        arguments: ODAFC argument list

    Raises:
        odafc.UnsupportedPlatform: for unsupported platforms
        odafc.ODAFCNotInstalledError: ODA File Converter not installed

    """
    if system == "Linux":
        with _linux_dummy_display() as display:
            env = os.environ.copy()
            env["DISPLAY"] = display
            proc = subprocess.Popen(
                [command] + arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            proc.wait()

    elif system == "Darwin":
        # TODO: unknown how to prevent the GUI from appearing on OSX
        proc = subprocess.Popen(
            [command] + arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.wait()

    elif system == "Windows":
        # New code from George-Jiang to solve the GUI pop-up problem
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = (
            subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        )
        startupinfo.wShowWindow = subprocess.SW_HIDE
        proc = subprocess.Popen(
            [command] + arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
        )
        proc.wait()
    else:
        # ODAFileConverter only has Linux, OSX and Windows versions
        raise UnsupportedPlatform(f"Unsupported platform: {system}")
    return proc


def _odafc_failed(system: str, proc: subprocess.Popen, stderr: str) -> bool:
    if proc.returncode != 0:
        # note: currently, ODAFileConverter does not set the return code
        return True

    stderr = stderr.strip()
    if system == "Linux":
        # ODAFileConverter *always* crashes on Linux even if the output was successful
        return stderr != "" and stderr != "Quit (core dumped)"
    else:
        return stderr != ""


def _execute_odafc(arguments: List[str]) -> Optional[bytes]:
    """ Execute ODAFC application.

    Args:
        arguments: ODAFC argument list

    Raises:
        odafc.ODAFCNotInstalledError: ODA File Converter not installed
        odafc.UnknownODAFCError: execution failed for unknown reasons
        odafc.UnsupportedPlatform: for unsupported platforms

    """
    logger.debug(f"Running ODAFileConverter with arguments: {arguments}")
    system = platform.system()
    oda_fc = _get_odafc_path(system)
    proc = _run_with_no_gui(system, oda_fc, arguments)
    stdout = proc.stdout.read().decode("utf-8")
    stderr = proc.stderr.read().decode("utf-8")

    if _odafc_failed(system, proc, stderr):
        msg = (
            f"ODA File Converter failed: return code = {proc.returncode}.\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
        logger.debug(msg)
        raise UnknownODAFCError(msg)
    return proc.stdout
