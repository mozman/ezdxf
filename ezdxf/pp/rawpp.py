# Purpose: Create a structured HTML view of raw DXF tags - not a CAD drawing!
# Created: 17.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
"""Creates a structured HTML view of raw DXF tags - not a CAD drawing!
"""
from __future__ import unicode_literals
from ezdxf.tools.c23 import escape, ustr
from ezdxf.lldxf.tags import group_tags
from .dxfpp import tag_type_str, GROUP_MARKERS, load_resource

TAG_TPL = '<div class="dxf-tag" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
          ' <span class="tag-value">{value}</span></div>'
MARKER_TPL = '<div class="tag-group-marker">{tag}</div>'
CONTROL_TPL = '<div class="tag-control-tag">{tag}</div>'


def rawpp(tagger, filename):
    def tag2html(tag):
        type_str = tag_type_str(tag.code)
        return TAG_TPL.format(code=tag.code, value=escape(ustr(tag.value)), type=escape(type_str))

    def marker(tag, tag_html):
        if tag.code == 0:
            return CONTROL_TPL.format(tag=tag_html)
        elif tag.code in GROUP_MARKERS:
            return MARKER_TPL.format(tag=tag_html)
        else:
            return tag_html

    def tags2html(tags):
        return '\n'.join(marker(tag, tag2html(tag)) for tag in tags)

    def groups(tags):
        for group in group_tags(tags, splitcode=0):
            yield '<div class="dxf-tag-group">\n{content}\n</div>'.format(content=tags2html(group))

    def dxf_control_structures(tags):
        return '\n'.join(groups(tags))

    template = load_resource('rawpp.html')
    return template.format(
        name=filename,
        css=load_resource('rawpp.css'),
        dxf_file=dxf_control_structures(tagger),
    )
