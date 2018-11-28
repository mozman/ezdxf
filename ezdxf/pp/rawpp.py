# Purpose: Create a structured HTML view of raw DXF tags - not a CAD drawing!
# Created: 17.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
"""
Creates a structured HTML view of raw DXF tags - not a CAD drawing!
"""

from ezdxf.tools import escape
from ezdxf.lldxf.tags import group_tags
from ezdxf.lldxf.types import GROUP_MARKERS, BINARY_FLAGS, HEX_HANDLE_CODES

from .dxfpp import tag_type_str, load_resource, with_bitmask, MAX_STR_LEN

TAG_TPL = '<div class="dxf-tag" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
          ' <span class="tag-value">{value}</span></div>'
MARKER_TPL = '<div class="tag-group-marker">{tag}</div>'
CONTROL_TPL = '<div class="tag-control-tag">{tag}</div>'


def rawpp(tagger, filename):
    def tag2html(tag):
        type_str = tag_type_str(tag.code)
        if tag.code in BINARY_FLAGS:
            vstr = with_bitmask(tag.value)
        else:
            vstr = str(tag.value)
            if tag.code in HEX_HANDLE_CODES:
                vstr = '#' + vstr
        if len(vstr) > MAX_STR_LEN:
            vstr = vstr[:MAX_STR_LEN-3] + '...'
        return TAG_TPL.format(code=tag.code, value=escape(vstr), type=escape(type_str))

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
