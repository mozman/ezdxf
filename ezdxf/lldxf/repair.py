# Purpose: repair/setup required DXF structures in existing DXF files (created by other DXF libs)
# Created: 05.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License

# Welcome to the place, where it gets dirty and ugly!

from ..modern.layouts import Layout
from .classifiedtags import ClassifiedTags
from .tags import DXFTag


def setup_model_space(dwg):
    setup_layout_space(dwg, 'Model', '*Model_Space', _MODEL_SPACE_LAYOUT_TPL)


def setup_paper_space(dwg):
    setup_layout_space(dwg, 'Layout1', '*Paper_Space', _PAPER_SPACE_LAYOUT_TPL)


def setup_layout_space(dwg, layout_name, block_name, tag_strimg):
    # This is just necessary for not existing DXF drawings without properly setup management structures.
    # Layout structure is not setup in this runtime phase
    layout_dict = dwg.dxffactory.wrap_handle(dwg.rootdict['ACAD_LAYOUT'])
    try:
        block_record = dwg.block_records.get(block_name)
    except KeyError:
        raise NotImplementedError("'%s' block record setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file." % block_name)
    block_record_handle = block_record.dxf.handle

    try:
        block = dwg.blocks.get(block_name)
    except KeyError:
        raise NotImplementedError("'%s' block setup not implemented, send an email to "
                                  "<mozman@gmx.at> with your DXF file." % block_name)
    else:
        block.set_block_record_handle(block_record_handle)   # grant valid linking

    layout_handle = create_layout_tags(dwg, block_record_handle, owner=layout_dict.dxf.handle, tag_string=tag_strimg)
    layout_dict[layout_name] = layout_handle  # insert layout into the layout management table
    block_record.dxf.layout = layout_handle  # link model space block record to layout


def create_layout_tags(dwg, block_record_handle, owner, tag_string):
    # Problem: ezdxf was not designed to handle the absence of model/paper space LAYOUT entities
    # Layout structure is not setup in this runtime phase

    object_section = dwg.objects
    entitydb = dwg.entitydb

    tags = ClassifiedTags.from_text(tag_string)
    layout_handle = entitydb.get_unique_handle()  # create new unique handle
    tags.replace_handle(layout_handle)  # set entity handle

    entitydb.add_tags(tags)  # add layout entity to entity database
    object_section.add_handle(layout_handle)  # add layout entity to objects section

    tags.noclass.set_first(330, owner)  # setup owner tag
    try:  # setup reactors
        acad_reactors = tags.get_appdata('{ACAD_REACTORS')
    except ValueError:
        pass
    else:
        acad_reactors.set_first(330, owner)

    acdblayout = tags.get_subclass('AcDbLayout')
    acdblayout.set_first(330, block_record_handle)  # link to block record
    return layout_handle


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
102
{ACAD_REACTORS
330
DEAD
102
}
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