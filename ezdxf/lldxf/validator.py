# Purpose: validate DXF tag structures
# Created: 03.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

import logging
import io

from .const import DXFStructureError, DXFError, DXFValueError, DXFAppDataError, DXFXDataError
from .const import APP_DATA_MARKER, HEADER_VAR_MARKER, XDATA_MARKER
from .const import INVALID_LAYER_NAME_CHARACTERS
from .tagger import low_level_tagger

logger = logging.getLogger('ezdxf')


def header_validator(tagger):
    """
    Checks the tag structure of the content of the header section.

    Do not feed (0, 'SECTION') (2, 'HEADER') and (0, 'ENDSEC') tags!

    Args:
        tagger: generator/iterator of low level tags or compiled tags

    Yields:
        DXFTag()

    Raises:
        DXFStructureError() -> invalid group codes
        DXFValueError() -> invalid header variable name
    """
    variable_name_tag = True
    for tag in tagger:
        if variable_name_tag:
            if tag.code != HEADER_VAR_MARKER:
                raise DXFStructureError('Invalid header variable tag ({0.code}, {0.value}).'.format(tag))
            if not tag.value.startswith('$'):
                raise DXFValueError('Invalid header variable name "{}", missing leading "$".'.format(tag.value))
            variable_name_tag = False
        else:
            variable_name_tag = True
        yield tag


def entity_structure_validator(tags):
    """
    Checks for valid DXF entity tag structure.

    - APP DATA can not be nested and every opening tag (102, '{...') needs a closing tag (102, '}')
    - extended group codes (>=1000) allowed before XDATA section
    - XDATA section starts with (1001, APPID) and is always at the end of an entity
    - XDATA section: only group code >= 1000 is allowed
    - XDATA control strings (1002, '{') and (1002, '}') have to be balanced

    XRECORD entities will not be checked.

    Args:
        tags: list of DXFTag()

    Yields:
        DXFTag()

    Raises:
        DXFAppDataError() for invalid APP DATA
        DXFXDataError() for invalid XDATA
    """
    assert isinstance(tags, list)
    dxftype = tags[0].value
    handle = '???'
    app_data = False
    xdata = False
    xdata_list_level = 0
    app_data_closing_tag = '}'
    for tag in tags:
        if tag.code == 5 and handle == '???':
            handle = tag.value
        if xdata:
            if tag.code < 1000:
                dxftype = tags[0].value
                raise DXFXDataError('Invalid XDATA structure in entity {}(#{}), only group code >=1000 allowed in XDATA section'.format(dxftype, handle))
            if tag.code == 1002:
                value = tag.value
                if value == '{':
                    xdata_list_level += 1
                elif value == '}':
                    xdata_list_level -= 1
                else:
                    raise DXFXDataError('Invalid XDATA control string (1002, "{}") entity {}(#{}).'.format(value, dxftype, handle))
                if xdata_list_level < 0:  # more closing than opening tags
                    raise DXFXDataError('Invalid XDATA structure in entity {}(#{}), unbalanced list markers, missing  (1002, "{{").'.format(dxftype, handle))

        if tag.code == APP_DATA_MARKER:
            value = tag.value
            if value.startswith('{'):
                if app_data:  # already in app data mode
                    raise DXFAppDataError('Invalid APP DATA structure in entity {}(#{}), APP DATA can not be nested.'.format(dxftype, handle))
                app_data = True
                # 'APPID}' is also a valid closing tag
                app_data_closing_tag = value[1:] + '}'
            elif value == '}' or value == app_data_closing_tag:
                if not app_data:
                    raise DXFAppDataError('Invalid APP DATA structure in entity {}(#{}), found (102, "}}") tag without opening tag.'.format(dxftype, handle))
                app_data = False
                app_data_closing_tag = '}'
            else:
                if dxftype != 'XRECORD':  # group code 102 as non app data allowed in XRECORD
                    raise DXFAppDataError('Invalid APP DATA structure tag (102, "{}") in entity {}(#{}).'.format(value, dxftype, handle))

        # XDATA section starts with (1001, APPID) and is always at the end of an entity
        if tag.code == XDATA_MARKER and xdata is False:
            xdata = True
            if app_data:
                raise DXFAppDataError('Invalid APP DATA structure in entity {}(#{}), missing closing tag (102, "}}").'.format(dxftype, handle))
        yield tag

    if app_data:
        raise DXFAppDataError('Invalid APP DATA structure in entity {}(#{}), missing closing tag (102, "}}").'.format(dxftype, handle))

    if xdata:
        if xdata_list_level < 0:
            raise DXFXDataError('Invalid XDATA structure in entity {}(#{}), unbalanced list markers, missing  (1002, "{{").'.format(dxftype, handle))
        elif xdata_list_level > 0:
            raise DXFXDataError('Invalid XDATA structure in entity {}(#{}), unbalanced list markers, missing  (1002, "}}").'.format(dxftype, handle))


def is_dxf_file(filename):
    with io.open(filename, errors='ignore') as fp:
        return is_dxf_stream(fp)


def is_dxf_stream(stream):
    try:
        reader = low_level_tagger(stream)
        return next(reader) == (0, 'SECTION')
    except DXFError:
        return False


def is_valid_layer_name(name):
    return not bool(INVALID_LAYER_NAME_CHARACTERS.intersection(set(name)))


is_valid_name = is_valid_layer_name


def is_adsk_special_layer(name):
    return name.upper().startswith('*ADSK_')  # special Autodesk layers starts with invalid character *
