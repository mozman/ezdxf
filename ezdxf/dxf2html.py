# Purpose: Create a structured HTML view of the DXF tags - not a CAD drawing!
# Created: 20.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
"""Creates a structured HTML view of the DXF tags - not a CAD drawing!
"""

import sys
import os

from ezdxf import readfile
from ezdxf.c23 import escape, ustr


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{name}.css">
<title>{name}.dxf</title>
</head>
<body>
<div class="dxf-file">
<h1>DXF-FILE: {name}.dxf</h1>
{body}
</div>
</body>
"""
TAG_TEMPLATE = '<div class="dxf-tag"><span class="tag-code">{code}</span><span class="tag-value">{value}</span></div>'
HDRVAR_TEMPLATE = '<div class="dxf-hdrvar"><span class="var-name">{name}</span> = <span class="var-value">{value}</span></div>'

def get_html_body(drawing):
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

    def hdrvars2html(hdrvars):
        def var2str(hdrvar):
            if hdrvar.ispoint:
                return  ustr(hdrvar.getpoint())
            else:
                return escape(ustr(hdrvar.value))

        varstrings = [HDRVAR_TEMPLATE.format(name=name, value=var2str(value)) for name, value in hdrvars.items()]
        return '<div class="dxf-hdrvars">\n{}\n</div>'.format("\n".join(varstrings))

    def tags2html(tags):
        return '<div class="dxf-tags">CONTENT: tags</div>'

    def entities2html(entities):
        return '<div class="dxf-entities">CONTENT: entities</div>'

    def tables2html(tables):
        return '<div class="dxf-tables">CONTENT: tables</div>'

    def blocks2html(blocks):
        return '<div class="dxf-blocks">CONTENT: blocks</div>'

    sections = [section2html(section) for section in drawing.sections]
    return "\n".join(sections)

def dxf2html(dwg):
    """ Creates a structured HTML view of the DXF tags - not a CAD drawing!
    """
    def get_name():
        if dwg.filename is None:
            return "unknown"
        else:
            filename = os.path.basename(dwg.filename)
            return os.path.splitext(filename)[0]

    return HTML_TEMPLATE.format(name=get_name(), body=get_html_body(dwg))

if __name__ == "__main__":
    dwg = readfile(sys.argv[1])
    html_filename = os.path.splitext(dwg.filename)[0] + '.html'
    with open(html_filename, mode='wt') as fp:
        fp.write(dxf2html(dwg))


