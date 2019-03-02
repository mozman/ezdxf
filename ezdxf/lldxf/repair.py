# Purpose: repair/setup required DXF structures in existing DXF files (created by other DXF libs)
# Created: 05.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
# --------------------------------------------------- #
# Welcome to the place, where it gets dirty and ugly! #
# --------------------------------------------------- #
from typing import TYPE_CHECKING, Iterable, Optional, List
from functools import partial
import logging

from .extendedtags import ExtendedTags
from .tags import DXFTag, Tags
from .types import POINT_CODES
from .const import DXFInternalEzdxfError, DXFValueError, DXFKeyError, SUBCLASS_MARKER, DXF12

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes import Drawing


def setup_layouts(dwg: 'Drawing'):
    layout_dict = dwg.rootdict.get_required_dict('ACAD_LAYOUT')
    if 'Model' not in layout_dict:  # do it only if model space is not defined
        setup_model_space(dwg)
        setup_paper_space(dwg)


def setup_model_space(dwg: 'Drawing'):
    setup_layout_space(dwg, 'Model', '*Model_Space', _MODEL_SPACE_LAYOUT_TPL)


def setup_paper_space(dwg: 'Drawing'):
    setup_layout_space(dwg, 'Layout1', '*Paper_Space', _PAPER_SPACE_LAYOUT_TPL)


def setup_layout_space(dwg: 'Drawing', layout_name: str, block_name: str, tag_string: str):
    # This is just necessary for existing DXF drawings without properly setup management structures.
    # Layout structure is not initialized at this runtime phase
    logger.info('creating LAYOUT structure for: {}'.format(layout_name))

    def get_block_record_by_alt_names(names: Iterable[str]):
        for name in names:
            try:
                brecord = dwg.block_records.get(name)
            except DXFValueError:
                pass
            else:
                return brecord
        raise DXFKeyError

    layout_dict = dwg.rootdict.get_required_dict('ACAD_LAYOUT')
    if layout_name in layout_dict:
        return
    try:
        block_record = get_block_record_by_alt_names((block_name, block_name.upper()))
    except DXFKeyError:
        raise NotImplementedError("'%s' block record setup not implemented, send an email to "
                                  "<ezdxf@mozman.at> with your DXF file." % block_name)
    real_block_name = block_record.dxf.name  # can be *Model_Space or *MODEL_SPACE
    block_record_handle = block_record.dxf.handle
    logger.debug('found {}: {}'.format(str(block_record), real_block_name))

    try:
        block_layout = dwg.blocks.get(real_block_name)
        logger.debug('found {}: {}'.format(str(block_layout.block), real_block_name))
    except DXFKeyError:
        logger.debug('expected BLOCK: {} not found.'.format(real_block_name))
        raise NotImplementedError("'%s' block setup not implemented, send an email to "
                                  "<ezdxf@mozman.at> with your DXF file." % real_block_name)
    else:
        block_layout.set_block_record_handle(block_record_handle)  # grant valid linking

    layout_handle = create_layout_tags(dwg, block_record_handle, owner=layout_dict.dxf.handle, tag_string=tag_string)
    logger.debug('creating entry in ACAD_LAYOUT dictionary for {}'.format(layout_name))
    layout_dict[layout_name] = layout_handle  # insert layout into the layout management table
    block_record.dxf.layout = layout_handle  # link model space block record to layout

    # rename block to standard format (*Model_Space or *Paper_Space)
    if real_block_name != block_name:
        logger.debug('renaming BLOCK form {} to {}'.format(block_name, real_block_name))
        dwg.blocks.rename_block(real_block_name, block_name)


def create_layout_tags(dwg: 'Drawing', block_record_handle: str, owner: str, tag_string: str):
    # Problem: ezdxf was not designed to handle the absence of model/paper space LAYOUT entities
    # Layout structure is not initialized at this runtime phase
    logger.debug('creating LAYOUT entity for BLOCK_RECORD(#{})'.format(block_record_handle))
    object_section = dwg.objects
    entitydb = dwg.entitydb

    tags = ExtendedTags.from_text(tag_string)
    layout_handle = entitydb.get_unique_handle()  # create new unique handle
    tags.replace_handle(layout_handle)  # set entity handle

    entitydb.add_tags(tags)  # add layout entity to entity database
    object_section.add_handle(layout_handle)  # add layout entity to objects section

    tags.noclass.set_first(DXFTag(330, owner))  # set owner tag
    acdblayout = tags.get_subclass('AcDbLayout')
    acdblayout.set_first(DXFTag(330, block_record_handle))  # link to block record
    return layout_handle


def upgrade_to_ac1015(dwg: 'Drawing'):
    """
    Upgrade DXF versions AC1012 and AC1014 to AC1015.
    """

    def upgrade_layout_table():
        if 'ACAD_LAYOUT' in dwg.rootdict:
            setup_model_space(dwg)  # setup layout entity and link to proper block and block_record entities
            setup_paper_space(dwg)  # setup layout entity and link to proper block and block_record entities
        else:
            raise DXFInternalEzdxfError("Table ACAD_LAYOUT should already exist in root dict.")

    def upgrade_layer_table():
        logger.debug('upgrading LAYERS table')
        try:
            plot_style_name_handle = dwg.rootdict.get('ACAD_PLOTSTYLENAME')  # DXFDictionaryWithDefault
        except DXFKeyError:
            raise DXFInternalEzdxfError("Table ACAD_PLOTSTYLENAME should already exist in root dict.")
        set_plot_style_name_in_layers(plot_style_name_handle)

        try:  # do not plot DEFPOINTS layer or AutoCAD is yelling
            defpoints_layer = dwg.layers.get('DEFPOINTS')
        except DXFValueError:
            pass
        else:
            defpoints_layer.dxf.plot = 0

    def set_plot_style_name_in_layers(plot_style_name_handle):
        logger.debug('setting layers "plot_style_name" attribute')
        for layer in dwg.layers:
            layer.dxf.plot_style_name = plot_style_name_handle

    def upgrade_dim_style_table():
        logger.debug('upgrading DIMSTYLES table')
        dim_styles = dwg.dimstyles
        header = dim_styles._table_header
        dim_style_table = Tags([
            DXFTag(100, 'AcDbDimStyleTable'),
            DXFTag(71, len(dim_styles))
        ])
        for entry in dim_styles:
            dim_style_table.append(DXFTag(340, entry.dxf.handle))
        header.subclasses.append(dim_style_table)

    def upgrade_objects():
        logger.debug('upgrading ACDBPLACEHOLDER entities in the OBJECTS section')
        upgrade_acdbplaceholder(dwg.objects.query('ACDBPLACEHOLDER'))

    def upgrade_acdbplaceholder(entities):
        for entity in entities:
            entity.tags.subclasses = entity.tags.subclasses[0:1]  # remove subclass AcDbPlaceHolder

    # calling order is important!
    logger.info('Upgrading drawing to DXF R2000.')
    upgrade_layout_table()
    upgrade_layer_table()
    upgrade_dim_style_table()
    upgrade_objects()

    logger.debug('Setting DXF version to AC1015.')
    dwg.dxfversion = 'AC1015'
    dwg.header['$ACADVER'] = 'AC1015'


def upgrade_to_ac1009(dwg: 'Drawing'):
    """
    Upgrade DXF versions prior to AC1009 (R12) to AC1009.
    """
    logger.info('Upgrading drawing to DXF R12.')
    logger.debug('Setting DXF version to AC1009.')
    dwg.dxfversion = 'AC1009'
    dwg.header['$ACADVER'] = DXF12
    # as far I know, nothing else to do


def cleanup_r12(dwg: 'Drawing'):
    """
    Remove unsupported sections and tables, repair tag structure.

    Args:
        dwg: Drawing() object

    """
    logger.info('Cleanup DXF R12 drawing.')
    if dwg.dxfversion > DXF12:
        return
    for section_name in ('CLASSES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA'):  # unsupported sections for DXF R12
        if section_name in dwg.sections:
            logger.debug('Deleting {} section.'.format(section_name))
            dwg.sections.delete_section(section_name)
    if 'BLOCK_RECORDS' in dwg.sections.tables:
        logger.debug('Deleting BLOCK_RECORDS table.')
        del dwg.sections.tables['BLOCK_RECORDS']


def filter_subclass_marker(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """
    Filter subclass marker from malformed DXF R12 files. (like from Leica Disto Units)

    Subclass markers in R12 files, creates subclasses in ExtendedTags(), which does not work with the DXF R12 attribute
    definitions. Other unsupported tags are not problematic, they are just ignored.

    Args:
        tagger: low level tagger

    """
    found = 0
    for tag in tagger:
        if tag.code == SUBCLASS_MARKER and tag.value.startswith('AcDb'):
            found += 1
        else:
            yield tag
    if found:
        logger.debug('Filtered {} SUBCLASS marker from DXF R12 tag stream.'.format(found))


def tag_reorder_layer(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """
    Reorder coordinates of legacy DXF Entities, for now only LINE.

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


def filter_out_of_order_point_codes(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """
    Filter point group codes if out of order e.g. 10, 20, 30, 20!

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


def fix_classes(dwg):
    def remove_group_code_91():
        logger.debug('Deleting group code 91 tags from CLASS entities for DXF Versions prior AC1018.')
        for cls in dwg.sections.classes:
            xtags = cls.tags
            xtags.noclass.remove_tags((91,))

    if dwg.dxfversion <= 'AC1009':  # DXF R12 and prior has no CLASSES
        return

    if dwg.dxfversion < 'AC1018':
        # remove group code 91, which is not supported prior to AC1018
        remove_group_code_91()


_MODEL_SPACE_LAYOUT_TPL = """  0
LAYOUT
  5
0
330
0
100
AcDbPlotSettings
  1

  2
DWFx ePlot (XPS Compatible).pc3
  4
ANSI_A_(8.50_x_11.00_Inches)
  6

 40
5.8
 41
17.8
 42
5.8
 43
17.8
 44
215.9
 45
279.4
 46
0.0
 47
0.0
 48
0.0
 49
0.0
140
0.0
141
0.0
142
1.0
143
14.53
 70
11952
 72
0
 73
1
 74
0
  7

 75
0
147
0.069
148
114.98
149
300.29
100
AcDbLayout
  1
Model
 70
1
 71
0
 10
0.0
 20
0.0
 11
12.0
 21
9.0
 12
0.0
 22
0.0
 32
0.0
 14
0.0
 24
0.0
 34
0.0
 15
0.0
 25
0.0
 35
0.0
146
0.0
 13
0.0
 23
0.0
 33
0.0
 16
1.0
 26
0.0
 36
0.0
 17
0.0
 27
1.0
 37
0.0
 76
0
330
0
"""

_PAPER_SPACE_LAYOUT_TPL = """  0
LAYOUT
  5
DEAD
330
DEAD
100
AcDbPlotSettings
  1

  2
DWFx ePlot (XPS Compatible).pc3
  4
ANSI_A_(8.50_x_11.00_Inches)
  6

 40
5.8
 41
17.8
 42
5.8
 43
17.8
 44
215.9
 45
279.4
 46
0.0
 47
0.0
 48
0.0
 49
0.0
140
0.0
141
0.0
142
1.0
143
1.0
 70
688
 72
0
 73
1
 74
5
  7
acad.ctb
 75
16
147
1.0
148
0.0
149
0.0
100
AcDbLayout
  1
Layout1
 70
1
 71
1
 10
-0.7
 20
-0.23
 11
10.3
 21
8.27
 12
0.0
 22
0.0
 32
0.0
 14
0.63
 24
0.8
 34
0.0
 15
9.0
 25
7.2
 35
0.0
146
0.0
 13
0.0
 23
0.0
 33
0.0
 16
1.0
 26
0.0
 36
0.0
 17
0.0
 27
1.0
 37
0.0
 76
0
330
DEAD
"""
