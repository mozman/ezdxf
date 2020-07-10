# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Optional
import logging
import subprocess
import os
from pathlib import Path
import ezdxf
from ezdxf.drawing import Drawing
from ezdxf.lldxf.validator import is_dxf_file, dxf_info, is_binary_dxf_file, dwg_version

logger = logging.getLogger('ezdxf')

exec_path = r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
temp_path = os.environ['TMP'] or os.environ['TEMP']


class ODAFCError(IOError):
    pass


VERSION_MAP = {
    'R12': 'ACAD12',
    'R13': 'ACAD13',
    'R14': 'ACAD14',
    'R2000': 'ACAD2000',
    'R2004': 'ACAD2004',
    'R2007': 'ACAD2007',
    'R2010': 'ACAD2010',
    'R2013': 'ACAD2013',
    'R2018': 'ACAD2018',
    'AC1004': 'ACAD9',
    'AC1006': 'ACAD10',
    'AC1009': 'ACAD12',
    'AC1012': 'ACAD13',
    'AC1014': 'ACAD14',
    'AC1015': 'ACAD2000',
    'AC1018': 'ACAD2004',
    'AC1021': 'ACAD2007',
    'AC1024': 'ACAD2010',
    'AC1027': 'ACAD2013',
    'AC1032': 'ACAD2018',
}

VALID_VERSIONS = {
    'ACAD9', 'ACAD10', 'ACAD12', 'ACAD13', 'ACAD14',
    'ACAD2000', 'ACAD2004', 'ACAD2007', 'ACAD2010',
    'ACAD2013', 'ACAD2018',
}


def map_version(version: str) -> str:
    return VERSION_MAP.get(version.upper(), version.upper())


# ODA File Converter command line format:
# ---------------------------------------
# OdaFC "Input Folder" "Output Folder" version type recurse audit [filter]
# version - Output version: "ACAD9" - "ACAD2018"
# type - Output file type: "DWG", "DXF", "DXB"
# recurse - Recurse Input Folder: "0" or "1"
# audit - audit each file: "0" or "1"
# optional Input files filter: default "*.DWG,*.DXF"


def readfile(filename: str, version: str = None, audit=False) -> Optional[Drawing]:
    """
    Use an installed `ODA File Converter`_ to convert a DWG/DXB/DXF file into a temporary DXF file and load
    this file by `ezdxf`.

    Args:
        filename: file to load by ODA File Converter
        version: load file as specific DXF version, by default the same version as the source file or
                 if not detectable the latest by `ezdxf` supported version.
        audit: audit source file before loading

    """
    infile = Path(filename).absolute()
    if not infile.exists():
        raise FileNotFoundError(f"No such file or directory: '{infile}'")
    in_folder = infile.parent
    name = infile.name
    ext = infile.suffix.lower()

    tmp_folder = Path(temp_path).absolute()
    if not tmp_folder.exists():
        tmp_folder.mkdir()

    dxf_temp_file = (tmp_folder / name).with_suffix('.dxf')
    _version = 'ACAD2018'
    if ext == '.dxf':
        if is_binary_dxf_file(str(infile)):
            pass
        elif is_dxf_file(str(infile)):
            with open(filename, 'rt') as fp:
                info = dxf_info(fp)
                _version = VERSION_MAP[info.version]
    elif ext == '.dwg':
        _version = dwg_version(str(infile))
        if _version is None:
            raise ValueError('Unknown or unsupported DWG version.')
    else:
        raise ValueError(f"Unsupported file format: '{ext}'")

    if version is None:
        version = _version

    version = map_version(version)
    cmd = _odafc_cmd(name, str(in_folder), str(tmp_folder), fmt='DXF', version=version, audit=audit)
    _execute_odafc(cmd)

    if dxf_temp_file.exists():
        doc = ezdxf.readfile(str(dxf_temp_file))
        dxf_temp_file.unlink()
        doc.filename = infile.with_suffix('.dxf')
        return doc
    return None


def export_dwg(doc: Drawing, filename: str, version=None, audit=False) -> None:
    """
    Use an installed `ODA File Converter`_ to export a DXF document `doc` as a DWG file.

    Saves a temporary DXF file and convert this DXF file into a DWG file by the ODA File Converter.
    If `version` is not specified the DXF version of the source document is used.

    Args:
        doc: `ezdxf` DXF document as :class:`~ezdxf.drawing.Drawing` object
        filename: export filename of DWG file, extension will be changed to ``'.dwg'``
        version: export file as specific version, by default the same version as the source document.
        audit: audit source file by ODA File Converter at exporting

    """
    if version is None:
        version = doc.dxfversion
    export_version = VERSION_MAP[version]
    dwg_file = Path(filename).absolute()
    dxf_file = Path(temp_path) / dwg_file.with_suffix('.dxf').name

    # Save DXF document
    old_filename = doc.filename
    doc.saveas(dxf_file)
    doc.filename = old_filename

    out_folder = Path(dwg_file.parent)
    try:
        if out_folder.exists():
            cmd = _odafc_cmd(dxf_file.name, str(temp_path), str(out_folder), fmt='DWG', version=export_version,
                             audit=audit)
            _execute_odafc(cmd)
        else:
            raise FileNotFoundError(f"No such file or directory: '{str(out_folder)}'")
    finally:
        if dxf_file.exists():
            dxf_file.unlink()


def _odafc_cmd(filename: str, in_folder: str, out_folder: str, fmt: str = 'DXF', version='ACAD2013', audit=False):
    recurse = '0'
    audit = '1' if audit else '0'
    return [exec_path, in_folder, out_folder, version, fmt, recurse, audit, filename]


def _execute_odafc(cmd) -> Optional[bytes]:
    logger.debug(f'run="{cmd}"')
    # New code from George-Jiang to solve the GUI pop-up problem
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    result = subprocess.Popen(args=cmd, stdout=subprocess.PIPE, stderr=None, startupinfo=startupinfo)
    if result.returncode:
        msg = f'ODA File Converter returns error code: {result.returncode}'
        logger.debug(msg)
        raise ODAFCError(msg)
    return result.stdout
