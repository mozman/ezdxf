# Purpose: validate DXF tag structures
# Created: 03.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
import logging

from .const import DXFStructureError

logger = logging.getLogger('ezdxf')


def structure_validator(tagreader, filter=False):
    """
    DXF structure validator.

    Checks if the overall structure of the DXF file is valid, expects following DXF layout:

          0
        SECTION
          0
        ENDSEC
        ...
        multiple sections
        ...
          0
        EOF

    Raises DXFStructureError() for missing SECTION, ENDSEC and EOF tags, everything else
    is written as warning to the 'ezdxf' logger. Comments are ignored.

    Args:
        tagreader: generator yielding DXFTag() objects
        filter: if True remove tags outside sections

    Yields:
        DXFTag()
    """
    def check_if_inside_section():
        if inside_section:
            raise DXFStructureError(error_prefix + 'missing ENDSEC tag.')

    error_prefix = 'DXF Structure Error: '
    found_eof = False
    inside_section = False
    log_warning_for_outside_tags = True

    for tag in tagreader:
        if tag.code == 999:  # ignore comments, where ever they are
            yield tag
            continue

        # SECTION, ENSEC and EOF tags can not be inside a section
        outside_tag_check = True

        if tag.code == 0:
            value = tag.value
            if value == 'SECTION':
                check_if_inside_section()
                inside_section = True
                outside_tag_check = False
            elif value == 'ENDSEC':
                if not inside_section:
                    raise DXFStructureError(error_prefix + 'found ENDSEC tag without previous SECTION tag.')
                inside_section = False
                outside_tag_check = False
            elif value == 'EOF':
                check_if_inside_section()
                found_eof = True
                outside_tag_check = False

        if not inside_section and outside_tag_check:
            if log_warning_for_outside_tags:
                logger.warning('DXF Structure Warning: found tags outside a SECTION.')
                # just 1 warning for all tags outside of a section
                log_warning_for_outside_tags = False
                # just 1 warning for removing tags outside of sections
                if filter:
                    logger.warning('DXF Structure Warning: removing tags outside of SECTIONS.')
            if filter:  # do not yield outside section tags
                continue

        yield tag

    check_if_inside_section()
    if not found_eof:
        raise DXFStructureError(error_prefix+'EOF tag not found.')
