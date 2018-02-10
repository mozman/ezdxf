# Purpose: validate DXF tag structures
# Created: 03.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

import logging
import io

from .const import DXFStructureError, DXFError, DXFValueError, DXFAppDataError, DXFXDataError
from .const import APP_DATA_MARKER, HEADER_VAR_MARKER
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
    - XDATA has to be at the end of the entity and after XDATA starts only group code >= 1000 is allowed
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

    if tags[0].value == 'XRECORD':  # does not work with XRECORD
        for tag in tags:  # return tags does not work in pypy, supporting Python 2 is more and more annoying
            yield tag
        return

    app_data = False
    xdata = False
    xdata_list_level = 0
    for tag in tags:
        if xdata:
            if tag.code < 1000:
                raise DXFXDataError('Invalid XDATA structure, only group code >=1000 allowed in XDATA section')
            if tag.code == 1002:
                value = tag.value
                if value == '{':
                    xdata_list_level += 1
                elif value == '}':
                    xdata_list_level -= 1
                else:
                    raise DXFXDataError('Invalid XDATA control string (1002, "{}").'.format(value))
                if xdata_list_level < 0:  # more closing than opening tags
                    raise DXFXDataError('Invalid XDATA structure, unbalanced list markers, missing  (1002, "{").')

        if tag.code == APP_DATA_MARKER:
            value = tag.value
            if value.startswith('{'):
                if app_data:  # already in app data mode
                    raise DXFAppDataError('Invalid APP DATA structure, APP DATA can not be nested.')
                app_data = True
            elif value == '}':
                if not app_data:
                    raise DXFAppDataError('Invalid APP DATA structure, found (102, "}") tag without opening tag.')
                app_data = False
            else:
                raise DXFAppDataError('Invalid APP DATA structure tag (102, "{}").'.format(value))

        if tag.code >= 1000 and xdata is False:
            xdata = True
            if app_data:
                raise DXFAppDataError('Invalid APP DATA structure, missing closing tag (102, "}").')
        yield tag

    if app_data:
        raise DXFAppDataError('Invalid APP DATA structure, missing closing tag (102, "}").')

    if xdata:
        if xdata_list_level < 0:
            raise DXFXDataError('Invalid XDATA structure, unbalanced list markers, missing  (1002, "{").')
        elif xdata_list_level > 0:
            raise DXFXDataError('Invalid XDATA structure, unbalanced list markers, missing  (1002, "}").')


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


def is_adsk_special_layer(name):
    return name.upper().startswith('*ADSK_')  # special Autodesk layers starts with invalid character *
