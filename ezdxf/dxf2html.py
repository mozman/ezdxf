# Purpose:
# Created: 20.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: GPLv3
import sys
from ezdxf import readfile

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
{body}
</body>
"""

def get_html_body(drawing):
    def section2html(section):
        if section.name == 'header':
            return section_info(section) + hdrvars2html(section.hdrvars)
        elif section.name in ('classes', 'objects', 'entities'):
            return section_info(section) + entities2html(iter(section))
        elif section.name == 'tables':
            return section_info(section) + tables2html(iter(section))
        elif section.name == 'blocks':
            return section_info(section) + blocks2html(iter(section))
        else:
            return section_info(section) + tags2html(section.tags)

    def section_info(section):
        return "<p>SECTION-NAME: {}</p>\n".format(section.name)

    def hdrvars2html(hdrvars):
        return "<p>CONTENT: hdrvars<p>"

    def tags2html(tags):
        return "<p>CONTENT: tags<p>"

    def entities2html(entities):
        return "<p>CONTENT: entities<p>"

    def tables2html(tables):
        return "<p>CONTENT: tables<p>"

    def blocks2html(tables):
        return "<p>CONTENT: blocks<p>"

    sections = [section2html(section) for section in drawing.sections]
    return "\n".join(sections)

def dxf2html(dwg, outname=None):
    body = get_html_body(dwg)
    if outname is None:
        if dwg.filename is None:
            outname = "dxf2html.html"
        else:
            outname = dwg.filename + '.html'


    with open(outname, mode='wt') as fp:
        fp.write(HTML_TEMPLATE.format(title=outname, body=body))

if __name__ == "__main__":
    filename = sys.argv[1]
    dwg = readfile(filename)
    dxf2html(dwg)

