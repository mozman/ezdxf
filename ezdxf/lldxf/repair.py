# Purpose: repair/setup required DXF structures in existing DXF files (created by other DXF libs)
# Created: 05.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License

# Welcome to the place, where it gets dirty and ugly!

from ..modern.layouts import Layout
from .classifiedtags import ClassifiedTags
from .tags import DXFTag

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
5.793749809265136
 41
17.79375076293945
 42
5.793746948242187
 43
17.79376220703125
 44
215.8999938964844
 45
279.3999938964844
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
14.5331733075991
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
0.068808097091715
148
114.9814160680965
149
300.291024640228
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


def create_model_space_layout(object_section, block_record_handle):
    # Problem: ezdxf was not designed to handle the absence of model space layout

    dwg = object_section.drawing
    entitydb = dwg.entitydb

    tags = ClassifiedTags.from_text(_MODEL_SPACE_LAYOUT_TPL)
    layout_handle = entitydb.handles.next()  # create new unique handle
    tags.replace_handle(layout_handle)  # set entity handle

    entitydb.add_tags(tags)  # add layout entity to entity database
    object_section.add_handle(layout_handle)  # add layout entity to objects section

    acdblayout = tags.get_subclass('AcDbLayout')
    acdblayout.set_first(330, block_record_handle)  # link to block record
    return Layout(dwg, layout_handle)


def setup_model_space(dwg):
    # This is just necessary for not existing DXF drawings without properly setup management structures.
    # Layout structure is not setup in this runtime phase
    layout_dict = dwg.rootdict['ACAD_LAYOUT']
    try:
        model_space_block_record = dwg.block_records.get('*Model_Space')
    except KeyError:
        raise NotImplementedError("Model space block record setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file.")
    model_space_block_record_handle = model_space_block_record.dxf.handle

    try:
        model_space_block = dwg.blocks.get('*Model_Space')
    except KeyError:
        raise NotImplementedError("Model space block setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file.")
    else:
        model_space_block.set_block_record_handle(model_space_block_record_handle)   # grant valid linking

    layout = create_model_space_layout(dwg.objects, model_space_block_record_handle)
    layout_handle = layout.dxf.handle
    layout.dxf.owner = layout_dict.dxf.handle  # set layout management table as owner of the layout
    layout_dict['Model'] = layout_handle  # insert layout into the layout management table
    model_space_block_record.dxf.layout = layout_handle  # link model space block record to layout


def setup_paper_space(dwg):
    # This is just necessary for not existing DXF drawings without properly setup management structures.
    # Layout structure is not setup in this runtime phase
    layout_dict = dwg.rootdict['ACAD_LAYOUT']


def upgrade_to_ac1009(dwg):
    dwg.dxfversion = 'AC1009'
    dwg.header['$ACADVER'] = 'AC1009'
    # as far I know, nothing else to do


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
