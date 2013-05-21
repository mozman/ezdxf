# Purpose: Create a structured HTML view of the DXF tags - not a CAD drawing!
# Created: 20.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
"""Creates a structured HTML view of the DXF tags - not a CAD drawing!
"""

import sys
import os
import shutil
from ezdxf import readfile
from ezdxf.tags import tag_type
from ezdxf.c23 import escape, ustr

FILE_DEPENDENCIES = ("dxf2html.js", "dxf2html.css")

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="dxf2html.css">
<script src="dxf2html.js"></script>
<title>{name}.dxf</title>
</head>
<body>
<div id="dxf-file" class="dxf-file"><h1>DXF-FILE: {name}.dxf</h1>
{body}
</div>
</body>
"""
TAG_TEMPLATE = '<div class="dxf-tag"><span class="tag-code">{code} {type}</span> <span class="tag-value">{value}</span></div>'
HDRVAR_TEMPLATE = '<div class="dxf-tag"><span class="tag-code">{name} {type}</span> = <span class="tag-value">{value}</span></div>'
ENTITY_TEMPLATE = '<div class="dxf-entity"><h3>{name}</h3>\n{tags}\n</div>'

def drawing2html(dwg):
    """ Creates a structured HTML view of the DXF tags - not a CAD drawing!
    """
    def get_name():
        if dwg.filename is None:
            return "unknown"
        else:
            filename = os.path.basename(dwg.filename)
            return os.path.splitext(filename)[0]

    return HTML_TEMPLATE.format(name=get_name(), body=sections2html(dwg))

def sections2html(drawing):
    sections = [section2html(section) for section in drawing.sections]
    return '<div class="dxf-sections">\n{}\n</div>'.format("\n".join(sections))

def section2html(section):
    if section.name == 'header':
        return section_info(section).format(hdrvars2html(section.hdrvars))
    elif section.name in ('classes', 'objects', 'entities'):
        return section_info(section).format(entities2html(iter(section)))
    elif section.name == 'tables':
        return section_info(section).format(tables2html(iter(section)))
    elif section.name == 'blocks':
        return section_info(section).format(blocks2html(iter(section)))
    else:
        return section_info(section).format(tags2html(section.tags))

def section_info(section):
    return '<div class="dxf-section"><h2>SECTION: {}</h2>\n{{}}\n</div>\n'.format(section.name)

TAG_TYPES = {
    int: '<int>',
    float: '<float>',
    ustr: '<string>',
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
        HDRVAR_TEMPLATE.format(name=name, value=escape(var2str(value)), type=escape(vartype(value)))
        for name, value in hdrvars.items()
    ]
    return '<div id="dxf-header" class="dxf-header">\n{}\n</div>'.format("\n".join(varstrings))

def tags2html(tags):
    def tag2html(tag):
        return TAG_TEMPLATE.format(code=tag.code, value=escape(ustr(tag.value)), type=escape(tag_type_str(tag.code)))
    tag_strings = (tag2html(tag) for tag in tags)
    return '<div class="dxf-tags">\n{}\n</div>'.format('\n'.join(tag_strings))

def entities2html(entities):
    entity_strings = (entity2html(entity) for entity in entities)
    return '<div id="dxf-entities" class="dxf-entities">\n{}\n</div>'.format("\n".join(entity_strings))

def entity2html(entity):
    return ENTITY_TEMPLATE.format(name=entity.dxftype(), tags=tags2html(entity.tags))

def tables2html(tables):
    return '<div id="dxf-tables" class="dxf-tables">CONTENT: tables</div>'

def blocks2html(blocks):
    return '<div id="dxf-blocks" class="dxf-blocks">CONTENT: blocks</div>'

def copy_dependencies_to(dst_path):
    src_path = os.path.dirname(__file__)
    for filename in FILE_DEPENDENCIES:
        src = os.path.join(src_path, filename)
        dst = os.path.join(dst_path, filename)
        shutil.copy(src, dst)

if __name__ == "__main__":
    dwg = readfile(sys.argv[1])
    copy_dependencies_to(os.path.dirname(dwg.filename))
    html_filename = os.path.splitext(dwg.filename)[0] + '.html'
    with open(html_filename, mode='wt') as fp:
        fp.write(drawing2html(dwg))


