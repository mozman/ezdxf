#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from ezdxf.lldxf.validator import is_dxf_file
from pathlib import Path


def make_backup(source: Path, backup: Path):
    backup.unlink(missing_ok=True)
    source.rename(backup)


def restore_backup(backup: Path, target: Path):
    target.unlink(missing_ok=True)
    backup.rename(target)


def strip_comments(source: Path, target: Path, verbose=False) -> int:
    try:
        with open(source, "rb") as infile, open(target, "wb") as outfile:
            line_number = 1
            removed_tags = 0
            while True:
                try:
                    raw_code_str = infile.readline()
                except EOFError:
                    raw_code_str = b""
                except IOError as e:
                    print(f"IOError: {str(e)}")
                if raw_code_str == b"":  # regular end of file
                    return removed_tags
                try:
                    code = int(raw_code_str)
                except ValueError:
                    code = raw_code_str.strip()
                    code = code.decode(encoding="utf8", errors="ignore")
                    print(
                        f'CANCELED: "{target.name}" - found invalid '
                        f'group code "{code}" at line {line_number}.'
                    )
                    break
                try:
                    raw_value_str = infile.readline()
                except (IOError, EOFError):
                    raw_value_str = b""
                if raw_value_str == b"":
                    print(f'CANCELED: "{target.name}" - premature end of file.')
                    break

                line_number += 2
                if code != 999:
                    outfile.write(raw_code_str)
                    outfile.write(raw_value_str)
                else:
                    if verbose:
                        value = raw_value_str.strip()
                        value = value.decode(encoding="utf8", errors="ignore")
                        print(f'removing comment: "{value}"')
                    removed_tags += 1
        # non regular exit by break:
        restore_backup(source, target)
    except IOError as e:
        print(str(e))
    return -1


def strip(filename: str, comments=True, backup=False, verbose=False):
    if verbose:
        print(f'\nProcessing file: "{filename}"')
    try:
        if not is_dxf_file(filename):
            print(
                f'CANCELED: "{filename}" is not a DXF file, binary DXF files '
                f'are not supported.'
            )
            return
    except IOError as e:
        print(f"IOError: {str(e)}")
        return
    source_file = Path(filename)
    backup_file = source_file.with_suffix(".bak")
    if verbose:
        print(f'renaming "{source_file.name}" to "{backup_file.name}"')
    make_backup(source_file, backup_file)

    target_file = source_file
    source_file = backup_file
    if comments:
        if verbose:
            print(
                f'copying "{source_file.name}" to "{target_file.name}" without '
                f"comment tags"
            )
        removed_tags = strip_comments(source_file, target_file, verbose)
        if removed_tags > 0:
            tags = "tag" if removed_tags == 1 else "tags"
            print(
                f'DONE: "{target_file.name}" - {removed_tags} comment {tags} '
                f"removed"
            )
        elif removed_tags == 0:
            print(f'DONE: "{target_file.name}" - no comment tags found')

    if not backup:
        if verbose:
            print(f'deleting backup file "{backup_file.name}"')
        backup_file.unlink(missing_ok=True)
