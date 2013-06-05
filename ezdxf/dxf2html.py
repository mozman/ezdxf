#coding: utf-8
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
from ezdxf.reflinks import get_reference_link

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
GROUP_MARKERS = (GENERAL_MARKER, SUBCLASS_MARKER, APP_DATA_MARKER, EXT_DATA_MARKER)

# HTML templates
# Section
ALL_SECTIONS_TPL = '<div class="dxf-sections">\n{content}\n</div>'
COMMON_SECTION_TPL = '<div id="{this_id}" class="dxf-section">' \
                     '<div class="dxf-section-name">SECTION: {ref_link}</div>\n' \
                     '<div class="button-bar">{prev} {next} <a class="link-button" href="#section-links">top<a/></div>\n' \
                     '{{content}}\n</div>\n'
HEADER_SECTION_TPL = '<div id="dxf-header" class="dxf-header">\n{content}\n</div>'
TABLES_SECTION_TPL = '<div id="dxf-tables" class="dxf-tables">{content}</div>'
BLOCKS_SECTION_TPL = '<div id="dxf-blocks" class="dxf-blocks">\n{content}\n</div>'

# Section content
HEADER_VAR_TPL = '<div class="hdr-var" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
                 ' <span class="tag-value">{value}</span></div>'
TABLE_TPL = '<div id="{name}-table" class="dxf-table">\n' \
            '<div class="dxf-table-name">{ref_link}</div>\n{nav}\n{header}\n{entries}\n</div>'
ENTITIES_TPL = '<div class="dxf-entities">\n{}\n</div>'

# DXF Entities
ENTITY_TPL = '<div class="dxf-entity"><div class="dxf-entity-name">{name}</div>\n{tags}\n</div>'
BLOCK_TPL = '<div class="dxf-block">\n<div class="dxf-block-name">{name}</div>\n{block}\n{entities}\n{endblk}\n</div>'
TAG_LIST_TPL = '<div class="dxf-tags">\n{content}\n</div>'

# Basic Tags
TAG_TPL = '<div class="dxf-tag" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
          ' <span class="tag-value">{value}</span></div>'
TAG_HANDLE_DEF_TPL = '<div class="dxf-tag"><span id="{value}" class="tag-code">{code}</span>'\
                     ' <span class="var-type">{type}</span> <span class="tag-value">{value}</span></div>'
TAG_HANDLE_LINK_TPL = '<div class="dxf-tag"><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
                      ' <a class="tag-link" href="#{value}">{value}</a></div>'
MARKER_TPL = '<div class="tag-group-marker">{tag}</div>'

# Links
SECTION_LINKS_TPL = '<div class="button-bar">SECTION-LINKS: {buttons}</div>\n'
REF_LINK_TPL = '<a class="dxf-ref-link" href={target} target="_blank" ' \
               'title="Link to DXF-Reference provided by Autodesk®.">{name}</a>'
BUTTON_BAR_TPL = '<div class="button-bar">{content}</div>'
BUTTON_TPL = '<a class="link-button" href="#{target}">{name}</a>'

def build_ref_link_button(name):
    """Create a link-button for element *name* to the DXF reference.
    """
    link = get_reference_link(name)
    return REF_LINK_TPL.format(target=link, name=name)

def dxf2html(dwg):
    """Creates a structured HTML view of the DXF tags - not a CAD drawing!
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
        section_links=sections_link_bar(dwg),
    )

def sections2html(dwg):
    """Creates a <div> container of all DXF sections.
    """
    sections_html = []
    for index, section in enumerate(dwg.sections):
        section_template = create_section_html_template(section.name, index)
        sections_html.append(section2html(section, section_template))
    return ALL_SECTIONS_TPL.format(content="\n".join(sections_html))

def sections_link_bar(dwg):
    """Creates a <div> container as link bar to all DXF sections.
    """
    section_links = []
    for index, section in enumerate(dwg.sections):
        section_links.append(BUTTON_TPL.format(
            name=section.name.upper(),
            target=SECTION_ID.format(index)
        ))
    return SECTION_LINKS_TPL.format(buttons=' \n'.join(section_links))

def section2html(section, section_template):
    """Creates a <div> container of a specific DXF sections.
    """
    if section.name == 'header':
        return section_template.format(content=hdrvars2html(section.hdrvars))
    elif section.name == 'entities':
        return section_template.format(content=entities2html(iter(section), create_ref_links=True))
    elif section.name == 'classes':
        return section_template.format(content=entities2html(iter(section), create_ref_links=False))
    elif section.name == 'objects':
        return section_template.format(content=entities2html(iter(section), create_ref_links=True))
    elif section.name == 'tables':
        return section_template.format(content=tables2html(section))  # no iterator!
    elif section.name == 'blocks':
        return section_template.format(content=blocks2html(iter(section)))
    else:
        return section_template.format(content=tags2html(section.tags))

SECTION_ID = "section_{}"
def create_section_html_template(name, index):
    """Creates a section template with buttons to the previous and next section.
    """
    def nav_ids():
        return SECTION_ID.format(index-1), SECTION_ID.format(index), SECTION_ID.format(index+1)
    prev_id, this_id, next_id = nav_ids()
    prev_button = BUTTON_TPL.format(target=prev_id, name='previous')
    next_button = BUTTON_TPL.format(target=next_id, name='next')
    return COMMON_SECTION_TPL.format(
        ref_link= build_ref_link_button(name.upper()),
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
    """DXF header section as <div> container.
    """
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
        HEADER_VAR_TPL.format(code=name, value=escape(var2str(value)), type=escape(vartype(value)))
        for name, value in hdrvars.items()
    ]
    return HEADER_SECTION_TPL.format(content="\n".join(varstrings))

def tags2html(tags):
    """DXF tag list as <div> container.
    """
    def tag2html(tag):
        def trim_str(vstr):
            if len(vstr) > 90:
                vstr = vstr[:75] + " ... " + vstr[-10:]
            return vstr

        tpl = TAG_TPL
        if tag.code in HANDLE_DEFINITIONS: # is handle definition
            tpl = TAG_HANDLE_DEF_TPL
        elif tag.code in HANDLE_LINKS: # is handle link
            tpl = TAG_HANDLE_LINK_TPL
        vstr = trim_str(ustr(tag.value))
        return tpl.format(code=tag.code, value=escape(vstr), type=escape(tag_type_str(tag.code)))

    def group_marker(tag, tag_html):
        return tag_html if tag.code not in GROUP_MARKERS else MARKER_TPL.format(tag=tag_html)

    tag_strings = (group_marker(tag, tag2html(tag)) for tag in tags)
    return TAG_LIST_TPL.format(content='\n'.join(tag_strings))

def entities2html(entities, create_ref_links=False):
    """DXF entities as <div> container.
    """
    entity_strings = (entity2html(entity, create_ref_links) for entity in entities)
    return ENTITIES_TPL.format("\n".join(entity_strings))

def entity2html(entity, create_ref_links=False):
    """DXF entity as <div> container.
    """
    if create_ref_links:  # use entity name as link to the DXF reference
        name = build_ref_link_button(entity.dxftype())
    else:
        name = entity.dxftype()
    return ENTITY_TPL.format(name=name, tags=tags2html(entity.tags))

def tables2html(tables):
    """DXF tables section as <div> container.
    """
    navigation = create_table_navigation(tables)
    tables_html_strings = [table2html(table, navigation) for table in tables]
    return TABLES_SECTION_TPL.format(content='\n'.join(tables_html_strings))

def create_table_navigation(table_section):
    """Create a button bar with links to all DXF tables as <div> container.
    """
    buttons = []
    for table in table_section:
        name = table.name.upper()
        link = "{}-table".format(name)
        buttons.append(BUTTON_TPL.format(name=name, target=link))
    return BUTTON_BAR_TPL.format(content="\n".join(buttons))

def table2html(table, navigation=''):
    """DXF table as <div> container.
    """
    header = ENTITY_TPL.format(name="TABLE HEADER", tags=tags2html(table._table_header))
    entries = entities2html(table)
    table_name = table.name.upper()
    return TABLE_TPL.format(name=table_name, ref_link=build_ref_link_button(table_name), nav= navigation, header=header,
        entries=entries)

def blocks2html(blocks):
    """DXF blocks section as <div> container.
    """
    block_strings = (block2html(block) for block in blocks)
    return BLOCKS_SECTION_TPL.format(content='\n'.join(block_strings))

def block2html(block_layout):
    """DXF block entity as <div> container.
    """
    block_html = entity2html(block_layout.block, create_ref_links=True)
    entities_html = entities2html(iter(block_layout), create_ref_links=True)
    endblk_html = entity2html(block_layout.endblk, create_ref_links=True)
    return BLOCK_TPL.format(name=block_layout.name, block=block_html, entities=entities_html, endblk=endblk_html)

def load_resource(filename):
    """Load external resource files.
    """
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