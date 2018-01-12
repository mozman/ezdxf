# Purpose: validate DXF tag structures
# Created: 03.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
import logging
import io

from .const import DXFStructureError, DXFError, DXFValueError
from .tagger import low_level_tagger, skip_comments

logger = logging.getLogger('ezdxf')


def structure_validator(tagger, filter=False):
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
        tagger: generator/iterator yielding DXFTag()
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

    for tag in tagger:
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


def header_validator(tagger):
    """
    Checks the tag structure of the content of the header section.

    Do not feed (0, 'SECTION') (2, 'HEADER') and (0, 'ENDSEC') tags!

    Args:
        tagger: generator/iterator yielding DXFTag()

    Yields:
        DXFTag()

    Raises:
        DXFStructureError() -> invalid group codes
        DXFValueError() -> invalid header variable name
    """
    variable_name_tag = True
    for tag in tagger:
        if variable_name_tag:
            if tag.code != 9:
                raise DXFStructureError('Invalid header variable tag ({0.code}, {0.value}).'.format(tag))
            if not tag.value.startswith('$'):
                raise DXFValueError('Invalid header variable name "{}", missing leading "$".'.format(tag.value))
            yield tag
            variable_name_tag = False
        else:
            yield tag
            variable_name_tag = True


def is_dxf_file(filename):
    with io.open(filename, errors='ignore') as fp:
        return is_dxf_stream(fp)


def is_dxf_stream(stream):
    try:
        reader = skip_comments(low_level_tagger(stream))
        return next(reader) == (0, 'SECTION')
    except DXFError:
        return False
