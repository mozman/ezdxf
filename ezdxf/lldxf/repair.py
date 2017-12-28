# Purpose: repair/setup required DXF structures in existing DXF files (created by other DXF libs)
# Created: 05.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
# --------------------------------------------------- #
# Welcome to the place, where it gets dirty and ugly! #
# --------------------------------------------------- #

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from datetime import datetime

from .classifiedtags import ClassifiedTags
from .tags import DXFTag, Tags
from .const import DXFInternalEzdxfError


def setup_layouts(dwg):
    layout_dict = dwg.rootdict.get_required_dict('ACAD_LAYOUT')
    if 'Model' not in layout_dict:  # do it only if model space is not defined
        setup_model_space(dwg)
        setup_paper_space(dwg)


def setup_model_space(dwg):
    setup_layout_space(dwg, 'Model', '*Model_Space', _MODEL_SPACE_LAYOUT_TPL)


def setup_paper_space(dwg):
    setup_layout_space(dwg, 'Layout1', '*Paper_Space', _PAPER_SPACE_LAYOUT_TPL)


def setup_layout_space(dwg, layout_name, block_name, tag_string):
    # This is just necessary for existing DXF drawings without properly setup management structures.
    # Layout structure is not initialized in this runtime phase
    def get_block_record_by_alt_names(names):
        for name in names:
            try:
                brecord = dwg.block_records.get(name)
            except ValueError:
                pass
            else:
                return brecord
        raise KeyError

    layout_dict = dwg.rootdict.get_required_dict('ACAD_LAYOUT')
    if layout_name in layout_dict:
        return
    try:
        block_record = get_block_record_by_alt_names((block_name, block_name.upper()))
    except KeyError:
        raise NotImplementedError("'%s' block record setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file." % block_name)
    real_block_name = block_record.dxf.name  # can be *Model_Space or *MODEL_SPACE
    block_record_handle = block_record.dxf.handle

    try:
        block = dwg.blocks.get(real_block_name)
    except KeyError:
        raise NotImplementedError("'%s' block setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file." % real_block_name)
    else:
        block.set_block_record_handle(block_record_handle)   # grant valid linking

    layout_handle = create_layout_tags(dwg, block_record_handle, owner=layout_dict.dxf.handle, tag_string=tag_string)
    layout_dict[layout_name] = layout_handle  # insert layout into the layout management table
    block_record.dxf.layout = layout_handle  # link model space block record to layout

    # rename block to standard format (*Model_Space or *Paper_Space)
    if real_block_name != block_name:
        dwg.blocks.rename_block(real_block_name, block_name)


def create_layout_tags(dwg, block_record_handle, owner, tag_string):
    # Problem: ezdxf was not designed to handle the absence of model/paper space LAYOUT entities
    # Layout structure is not initialized in this runtime phase

    object_section = dwg.objects
    entitydb = dwg.entitydb

    tags = ClassifiedTags.from_text(tag_string)
    layout_handle = entitydb.get_unique_handle()  # create new unique handle
    tags.replace_handle(layout_handle)  # set entity handle

    entitydb.add_tags(tags)  # add layout entity to entity database
    object_section.add_handle(layout_handle)  # add layout entity to objects section

    tags.noclass.set_first(330, owner)  # set owner tag
    acdblayout = tags.get_subclass('AcDbLayout')
    acdblayout.set_first(330, block_record_handle)  # link to block record
    return layout_handle


def upgrade_to_ac1015(dwg):
    """Upgrade DXF versions AC1012 and AC1014 to AC1015.
    """
    def upgrade_layout_table():
        if 'ACAD_LAYOUT' in dwg.rootdict:
            setup_model_space(dwg)  # setup layout entity and link to proper block and block_record entities
            setup_paper_space(dwg)  # setup layout entity and link to proper block and block_record entities
        else:
            raise DXFInternalEzdxfError("Table ACAD_LAYOUT should already exist in root dict.")

    def upgrade_layer_table():
        try:
            plot_style_name_handle = dwg.rootdict.get('ACAD_PLOTSTYLENAME')  # DXFDictionaryWithDefault
        except KeyError:
            raise DXFInternalEzdxfError("Table ACAD_PLOTSTYLENAME should already exist in root dict.")
        set_plot_style_name_in_layers(plot_style_name_handle)

        try:  # do not plot DEFPOINTS layer or AutoCAD is yelling
            defpoints_layer = dwg.layers.get('DEFPOINTS')
        except ValueError:
            pass
        else:
            defpoints_layer.dxf.plot = 0

    def set_plot_style_name_in_layers(plot_style_name_handle):
        for layer in dwg.layers:
            layer.dxf.plot_style_name = plot_style_name_handle

    def upgrade_dim_style_table():
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
        upgrade_acdbplaceholder(dwg.objects.query('ACDBPLACEHOLDER'))

    def upgrade_acdbplaceholder(entities):
        for entity in entities:
            entity.tags.subclasses = entity.tags.subclasses[0:1]  # remove subclass AcDbPlaceHolder

    # calling order is important!
    upgrade_layout_table()
    upgrade_layer_table()
    upgrade_dim_style_table()
    upgrade_objects()

    add_upgrade_comment(dwg, dwg.dxfversion, 'AC1015 (R2000)')
    dwg.dxfversion = 'AC1015'
    dwg.header['$ACADVER'] = 'AC1015'


def upgrade_to_ac1009(dwg):
    """Upgrade DXF versions prior to AC1009 (R12) to AC1009.
    """
    add_upgrade_comment(dwg, dwg.dxfversion, 'AC1009 (R12)')
    dwg.dxfversion = 'AC1009'
    dwg.header['$ACADVER'] = 'AC1009'
    # as far I know, nothing else to do


def add_upgrade_comment(dwg, from_version, to_version):
    """Upgrade DXF versions prior to AC1009 (R12) to AC1009.
    """
    from .. import VERSION
    dwg.dxfversion = 'AC1009'
    dwg.comments.append("DXF version upgrade from {f} to {t} by ezdxf {v} on {dt}".format(
        f=from_version,
        t=to_version,
        v=VERSION,
        dt=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def enable_handles(dwg):
    """ Enable 'handles' for DXF R12 to be consistent with later DXF versions.

    Write entitydb-handles into entity-tags.
    """
    def has_handle(tags, handle_code):
        for tag in tags.noclass:
            if tag.code == handle_code:
                return True
        return False

    def put_handles_into_entity_tags():
        for handle, tags in dwg.entitydb.items():
            is_not_dimstyle = tags.noclass[0] != (0, 'DIMSTYLE')
            handle_code = 5 if is_not_dimstyle else 105  # legacy shit!!!
            if not has_handle(tags, handle_code):
                tags.noclass.insert(1, DXFTag(handle_code, handle))  # handle should be the 2. tag

    if dwg.dxfversion > 'AC1009':
        return
    put_handles_into_entity_tags()
    dwg.header['$HANDLING'] = 1


def repair_leica_disto_r12(dwg):
    """ Repairs DXF R12 files generated by Leica Disto Units.

    The base file format is DXF R12, but with subclass markers like (100, AcDbEntity), which were introduced with
    DXF R13. ezdxf does not ignore this subclass markers and creates this subclasses, which are not seen by the legacy
    (DXF R12) DXF engine. This function merges all subclasses into the noclass subclass (tags.subclasses[0]) and removes
    the subclass markers, which leads to a full DXF R12 compatible file structure.

    :param dwg: ezdxf Drawing() class
    """
    if dwg.dxfversion > 'AC1009':
        return  # do not repair DXF R13 or later DXF versions
    for entity in dwg.entities:
        join_subclasses(entity.tags.subclasses)
    if 'block_records' in dwg.sections.tables:  # remove unsupported block_records table
        del dwg.sections.tables['block_records']

    from .. import VERSION
    dwg.comments.append("malformed DXF R12 file repaired by ezdxf {v}".format(v=VERSION))


def join_subclasses(subclasses):
    if len(subclasses) > 1:
        noclass = subclasses[0]
        for subclass in subclasses[1:]:
            noclass.extend(subclass[1:])
        del subclasses[1:]


def is_leica_disto_r12(dwg):
    if dwg.dxfversion > 'AC1009':
        return False
    for entity in dwg.entities:  # test only the first entity
        if len(entity.tags.subclasses) > 1:  # if DXF R12 file have subclass markers
            return True
        else:
            return False


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
