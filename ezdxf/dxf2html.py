# Purpose: Create a structured HTML view of the DXF tags - not a CAD drawing!
# Created: 20.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
"""Creates a structured HTML view of the DXF tags - not a CAD drawing!
"""

import sys
import os
import io

from ezdxf import readfile
from ezdxf.tags import tag_type
from ezdxf.c23 import escape, ustr

# Handle definitions
_HANDLE_CODES = [5, 105]
_HANDLE_CODES.extend(range(320, 330))
HANDLE_DEFINITIONS = frozenset(_HANDLE_CODES)

# Handle links
_HANDLE_POINTERS = list(range(330, 370))
_HANDLE_POINTERS.extend((480, 481, 1005))
HANDLE_LINKS = frozenset(_HANDLE_POINTERS)

# Tag groups
GENERAL_MARKER = 0
SUBCLASS_MARKER = 100
APP_DATA_MARKER = 102
EXT_DATA_MARKER = 1001
GROUP_MARKERS = (GENERAL_MARKER,SUBCLASS_MARKER, APP_DATA_MARKER, EXT_DATA_MARKER)
MARKER_TEMPLATE = '<div class="tag-group-marker">{tag}</div>'

HEADER_VAR_TEMPLATE = '<div class="hdr-var" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span> <span class="tag-value">{value}</span></div>'
TAG_TEMPLATE = '<div class="dxf-tag" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span> <span class="tag-value">{value}</span></div>'
TAG_TEMPLATE_HANDLE_DEF = '<div class="dxf-tag"><span id="{value}" class="tag-code">{code}</span> <span class="var-type">{type}</span> <span class="tag-value">{value}</span></div>'
TAG_TEMPLATE_HANDLE_LINK = '<div class="dxf-tag"><span class="tag-code">{code}</span> <span class="var-type">{type}</span> <a class="tag-value" href="#{value}">{value}</a></div>'

ENTITY_TEMPLATE = '<div class="dxf-entity"><div class="dxf-entity-name">{name}</div>\n{tags}\n</div>'

TOC_TPL = '<div class="button-bar">{buttons}</div>\n'

BUTTON_TPL = '<a href="#{target}">{name}</a>'

def dxf2html(dwg):
    """ Creates a structured HTML view of the DXF tags - not a CAD drawing!
    """
    def get_name():
        if dwg.filename is None:
            return "unknown"
        else:
            filename = os.path.basename(dwg.filename)
            return os.path.splitext(filename)[0]
    template = load_resource('dxf2html.html')
    return template.format(
        name=get_name(),
        css=load_resource('dxf2html.css'),
        javascript=load_resource('dxf2html.js'),
        dxf_file=sections2html(dwg),
        toc=sections_toc_as_html(dwg),
    )

def sections2html(dwg):
    sections_html = []
    for index, section in enumerate(dwg.sections):
        section_template = create_section_html_template(section.name, index)
        sections_html.append(section2html(section, section_template))
    return '<div class="dxf-sections">\n{}\n</div>'.format("\n".join(sections_html))

def sections_toc_as_html(dwg):
    toc_entries = []
    for index, section in enumerate(dwg.sections):
        toc_entries.append(BUTTON_TPL.format(
            name=section.name.upper(),
            target=SECTION_ID.format(index)
        ))
    return TOC_TPL.format(buttons=' \n'.join(toc_entries))

def section2html(section, section_template):
    if section.name == 'header':
        return section_template.format(hdrvars2html(section.hdrvars))
    elif section.name in ('classes', 'objects', 'entities'):
        return section_template.format(entities2html(iter(section)))
    elif section.name == 'tables':
        return section_template.format(tables2html(section))  # no iterator
    elif section.name == 'blocks':
        return section_template.format(blocks2html(iter(section)))
    else:
        return section_template.format(tags2html(section.tags))

SECTION_ID = "section_{}"
def create_section_html_template(name, index):
    def nav_ids():
        return SECTION_ID.format(index-1), SECTION_ID.format(index), SECTION_ID.format(index+1)
    prev_id, this_id, next_id = nav_ids()
    prev_button = BUTTON_TPL.format(target=prev_id, name='previous')
    next_button = BUTTON_TPL.format(target=next_id, name='next')
    return '<div id="{this_id}" class="dxf-section"><div class="dxf-section-name">SECTION: {name}</div>\n'\
           '<div class="button-bar">{prev} {next}</div>\n{{}}\n</div>\n'.format(
        name=name.upper(),
        this_id=this_id,
        prev=prev_button,
        next=next_button)

TAG_TYPES = {
    int: '<int>',
    float: '<float>',
    ustr: '<str>',
}

def tag_type_str(code):
    return TAG_TYPES[tag_type(code)]

def hdrvars2html(hdrvars):
    def var2str(hdrvar):
        if hdrvar.ispoint:
            return  ustr(hdrvar.getpoint())
        else:
            return ustr(hdrvar.value)

    def vartype(hdrvar):
        if hdrvar.ispoint:
            dim = len(hdrvar.getpoint()) - 2
            return ("<point 2D>", "<point 3D>")[dim]
        else:
            return tag_type_str(hdrvar.code)


    varstrings = [
        HEADER_VAR_TEMPLATE.format(code=name, value=escape(var2str(value)), type=escape(vartype(value)))
        for name, value in hdrvars.items()
    ]
    return '<div id="dxf-header" class="dxf-header">\n{}\n</div>'.format("\n".join(varstrings))

def tags2html(tags):
    def tag2html(tag):
        tpl = TAG_TEMPLATE
        if tag.code in HANDLE_DEFINITIONS: # is handle definition
            tpl = TAG_TEMPLATE_HANDLE_DEF
        elif tag.code in HANDLE_LINKS: # is handle link
            tpl = TAG_TEMPLATE_HANDLE_LINK
        return tpl.format(code=tag.code, value=escape(ustr(tag.value)), type=escape(tag_type_str(tag.code)))

    def group_marker(tag, tag_html):
        return tag_html if tag.code not in GROUP_MARKERS else MARKER_TEMPLATE.format(tag=tag_html)

    tag_strings = (group_marker(tag, tag2html(tag)) for tag in tags)
    return '<div class="dxf-tags">\n{}\n</div>'.format('\n'.join(tag_strings))

def entities2html(entities):
    entity_strings = (entity2html(entity) for entity in entities)
    return '<div class="dxf-entities">\n{}\n</div>'.format("\n".join(entity_strings))

def entity2html(entity):
    return ENTITY_TEMPLATE.format(name=entity.dxftype(), tags=tags2html(entity.tags))

def tables2html(tables):
    navigation = create_table_navigation(tables)
    tables_html_strings = [table2html(table, navigation) for table in tables]
    return '<div id="dxf-tables" class="dxf-tables">{}</div>'.format('\n'.join(tables_html_strings))

def create_table_navigation(table_section):
    buttons = []
    for table in table_section:
        name = table.name.upper()
        link = "{}-table".format(name)
        buttons.append(BUTTON_TPL.format(name=name, target=link))
    return '<div class="button-bar">{}</div>'.format("\n".join(buttons))

def table2html(table, navigation=''):
    header = ENTITY_TEMPLATE.format(name="TABLE HEADER", tags=tags2html(table._table_header))
    entries = entities2html(table)
    return '<div id="{name}-table" class="dxf-table">\n<div class="dxf-table-name">{name}</div>\n{nav}\n{header}\n{entries}\n</div>'.format(
        name=table.name.upper(),
        nav= navigation,
        header=header,
        entries=entries)

def blocks2html(blocks):
    block_strings = (block2html(block) for block in blocks)
    return '<div id="dxf-blocks" class="dxf-blocks">\n{}\n</div>'.format('\n'.join(block_strings))

def block2html(block_layout):
    block_html = entity2html(block_layout.block)
    entities_html = entities2html(iter(block_layout))
    endblk_html = entity2html(block_layout.endblk)
    return '<div class="dxf-block">\n<div class="dxf-block-name">{name}</div>\n{block}\n{entities}\n{endblk}\n</div>'.format(
        name=block_layout.name, block=block_html, entities=entities_html, endblk=endblk_html)

def load_resource(filename):
    src_path = os.path.dirname(__file__)
    src = os.path.join(src_path, filename)
    try:
        with io.open(src, mode="rt", encoding='utf-8') as fp:
            resource = fp.read()
    except IOError:
        errmsg = "IOError: can not read file '{}'.".format(src)
        print(errmsg)
        resource = errmsg
    return resource

if __name__ == "__main__":
    dwg = readfile(sys.argv[1])
    html_filename = os.path.splitext(dwg.filename)[0] + '.html'
    try:
        with io.open(html_filename, mode='wt', encoding='utf-8') as fp:
            fp.write(dxf2html(dwg))
    except IOError:
        print("IOError: can not write file '{}'.".format(html_filename))