#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import BinaryIO
from ezdxf.lldxf.validator import is_dxf_file, DXFStructureError
from pathlib import Path


class TagWriter:
    def __init__(self, fp: BinaryIO):
        self.fp = fp

    def write(self, raw_code_str: bytes, raw_value_str: bytes):
        self.fp.write(raw_code_str)
        self.fp.write(raw_value_str)


class ThumbnailRemover(TagWriter):
    def __init__(self, fp: BinaryIO):
        super().__init__(fp)
        self._start_section = False
        self._skip_tags = False
        self._section_code = None
        self._section_value = None
        self.removed_thumbnail_image = False

    def write(self, raw_code_str: bytes, raw_value_str: bytes):
        code = raw_code_str.strip()
        value = raw_value_str.strip()
        if self._start_section:
            self._start_section = False
            if code == b"2" and value == b"THUMBNAILIMAGE":
                self._skip_tags = True
                self.removed_thumbnail_image = True
            else:
                # write buffered section tag:
                super().write(self._section_code, self._section_value)

        if code == b"0":
            if value == b"SECTION":
                self._start_section = True
                self._skip_tags = False
                # buffer section tag:
                self._section_code = raw_code_str
                self._section_value = raw_value_str
                return
            elif value == b"ENDSEC":
                skip = self._skip_tags
                self._skip_tags = False
                if skip:  # don't write ENDSEC
                    return

        if not self._skip_tags:
            super().write(raw_code_str, raw_value_str)


def strip_comments(
    infile: BinaryIO, tagwriter: TagWriter, verbose=False
) -> int:
    line_number = 1
    removed_tags = 0
    while True:
        try:
            raw_code_str = infile.readline()
        except EOFError:
            raw_code_str = b""
        if raw_code_str == b"":  # regular end of file
            return removed_tags
        try:
            code = int(raw_code_str)
        except ValueError:
            code = raw_code_str.strip()
            code = code.decode(encoding="utf8", errors="ignore")
            raise DXFStructureError(
                f'CANCELED: "{infile.name}" - found invalid '
                f'group code "{code}" at line {line_number}'
            )

        try:
            raw_value_str = infile.readline()
        except EOFError:
            raw_value_str = b""

        if raw_value_str == b"":
            raise DXFStructureError(
                f'CANCELED: "{infile.name}" - premature end of file'
            )
        line_number += 2
        if code != 999:
            tagwriter.write(raw_code_str, raw_value_str)
        else:
            if verbose:
                value = raw_value_str.strip()
                value = value.decode(encoding="utf8", errors="ignore")
                print(f'removing comment: "{value}"')
            removed_tags += 1


def safe_rename(source: Path, target: Path, backup=True, verbose=False) -> bool:
    backup_file = target.with_suffix(".bak")
    backup_file.unlink(missing_ok=True)
    _target = Path(target)
    if _target.exists():
        if verbose:
            print(f'renaming "{_target.name}" to "{backup_file.name}"')
        try:
            _target.rename(backup_file)
        except IOError as e:
            print(f"IOError: {str(e)}")
            return False

    if verbose:
        print(f'renaming "{source.name}" to "{target.name}"')
    try:
        source.rename(target)
    except IOError as e:
        print(f"IOError: {str(e)}")
        return False

    if not backup:
        if verbose:
            print(f'deleting backup file "{backup_file.name}"')
        backup_file.unlink(missing_ok=True)


def strip(filename: str, backup=False, thumbnail=False, verbose=False):
    def remove_tmp_file():
        if tmp_file.exists():
            if verbose:
                print(f'deleting temp file: "{tmp_file.name}"')
            tmp_file.unlink(missing_ok=True)

    if verbose:
        print(f'\nProcessing file: "{filename}"')
    try:
        if not is_dxf_file(filename):
            print(
                f'CANCELED: "{filename}" is not a DXF file, binary DXF files '
                f"are not supported"
            )
            return
    except IOError as e:
        print(f"IOError: {str(e)}")
        return
    source_file = Path(filename)
    tmp_file = source_file.with_suffix(".ezdxf.tmp")
    error = False
    if verbose:
        print(f'make a temporary copy: "{tmp_file.name}"')
    with open(tmp_file, "wb") as fp, open(source_file, "rb") as infile:
        if thumbnail:
            tagwriter = ThumbnailRemover(fp)
        else:
            tagwriter = TagWriter(fp)
        try:
            removed_tags = strip_comments(infile, tagwriter, verbose)
        except IOError as e:
            print(f"IOError: {str(e)}")
            error = True
        except DXFStructureError as e:
            print(str(e))
            error = True

    if not error:
        rename = False
        if thumbnail and tagwriter.removed_thumbnail_image:
            print(f'"{source_file.name}" - removed THUMBNAILIMAGE section')
            rename = True

        if removed_tags > 0:
            tags = "tag" if removed_tags == 1 else "tags"
            print(
                f'"{source_file.name}" - {removed_tags} comment {tags} removed'
            )
            rename = True

        if rename:
            safe_rename(tmp_file, source_file, backup, verbose)

    remove_tmp_file()
