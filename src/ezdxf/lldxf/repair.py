# Created: 05.03.2016
# Copyright (c) 2016-2019, Manfred Moitzi
# License: MIT License
from typing import Iterable, Optional, List, TYPE_CHECKING
from functools import partial
import logging
from .tags import DXFTag
from .types import POINT_CODES

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags


def tag_reorder_layer(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """
    Reorder coordinates of legacy DXF Entities, for now only LINE.

    Input Raw tag filter.

    Args:
        tagger: low level tagger

    """
    logger.debug('Reordering coordinate tags for LINE entity.')
    collector = None  # type: Optional[List]
    for tag in tagger:
        if tag.code == 0:
            if collector is not None:  # stop collecting if inside of an supported entity
                entity = collector[0].value
                yield from COORDINATE_FIXING_TOOLBOX[entity](collector)
                collector = None

            if tag.value in COORDINATE_FIXING_TOOLBOX:
                collector = [tag]
                tag = None  # do not yield collected tag yet
        else:  # tag.code != 0
            if collector is not None:
                collector.append(tag)
                tag = None  # do not yield collected tag yet
        if tag is not None:
            yield tag


# invalid point codes if not part of a point started with 1010, 1011, 1012, 1013
INVALID_Y_CODES = {code + 10 for code in POINT_CODES}
INVALID_Z_CODES = {code + 20 for code in POINT_CODES}
INVALID_CODES = INVALID_Y_CODES | INVALID_Z_CODES
X_CODES = POINT_CODES


def filter_invalid_yz_point_codes(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """
    Filter point group codes if out of order e.g. 10, 20, 30, 20!

    Input Raw tag filter

    Args:
        tagger: low level tagger

    """
    logger.debug('Filtering out of order point codes.')
    expected_code = 0
    point = 0

    for tag in tagger:
        code = tag[0]
        if point and code == expected_code:
            expected_code += 10
            if expected_code - point > 20:
                point = 0
        else:
            point = 0
            if code in INVALID_CODES:
                continue
            if code in X_CODES:
                point = code
                expected_code = point + 10
        yield tag


def fix_coordinate_order(tags, codes=(10, 11)):
    def extend_codes():
        for code in codes:
            yield code  # x tag
            yield code + 10  # y tag
            yield code + 20  # z tag

    def get_coords(code):
        # if x or y coordinate is missing, it is a DXFStructureError
        # but here is not the location to validate the DXF structure
        try:
            yield coordinates[code]
        except KeyError:
            pass
        try:
            yield coordinates[code + 10]
        except KeyError:
            pass
        try:
            yield coordinates[code + 20]
        except KeyError:
            pass

    coordinate_codes = frozenset(extend_codes())
    coordinates = {}
    remaining_tags = []
    insert_pos = None
    for tag in tags:
        # separate tags
        if tag.code in coordinate_codes:
            coordinates[tag.code] = tag
            if insert_pos is None:
                insert_pos = tags.index(tag)
        else:
            remaining_tags.append(tag)

    if len(coordinates) == 0:
        # no coordinates found, this is probably a DXFStructureError,
        # but here is not the location to validate the DXF structure,
        # just do nothing.
        return tags

    ordered_coords = []
    for code in codes:
        ordered_coords.extend(get_coords(code))
    remaining_tags[insert_pos:insert_pos] = ordered_coords
    return remaining_tags


COORDINATE_FIXING_TOOLBOX = {
    'LINE': partial(fix_coordinate_order, codes=(10, 11)),
}

VALID_XDATA_CODES = set(range(1000, 1019)) | set(range(1040, 1072))


def filter_invalid_xdata_group_codes(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    for tag in tagger:
        if tag.code < 1000 or tag.code in VALID_XDATA_CODES:
            yield tag
