# Purpose: Create a structured HTML view of raw DXF tags - not a CAD drawing!
# Created: 17.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
"""
Creates a structured HTML view of raw DXF tags - not a CAD drawing!
"""
from typing import Iterable
from ezdxf.tools import escape
from ezdxf.lldxf.tags import group_tags, DXFTag
from ezdxf.lldxf.types import GROUP_MARKERS, BINARY_FLAGS, HEX_HANDLE_CODES
from ezdxf.tools.binarydata import bytes_to_hexstr
from .dxfpp import tag_type_str, load_resource, with_bitmask, MAX_STR_LEN

TAG_TPL = '<div class="dxf-tag" ><span class="tag-code">{code}</span> <span class="var-type">{type}</span>' \
          ' <span class="tag-value">{value}</span></div>'
MARKER_TPL = '<div class="tag-group-marker">{tag}</div>'
CONTROL_TPL = '<div class="tag-control-tag">{tag}</div>'


def rawpp(tagger: Iterable[DXFTag], filename: str, binary=False) -> str:
    def tag2html(tag: DXFTag) -> str:
        type_str = tag_type_str(tag.code)
        value = tag.value
        if tag.code in BINARY_FLAGS:
            vstr = with_bitmask(value)
        else:

            if isinstance(value, bytes):
                vstr = bytes_to_hexstr(value)
            else:
                vstr = str(tag.value)
                if tag.code in HEX_HANDLE_CODES:
                    vstr = '#' + vstr
        if len(vstr) > MAX_STR_LEN:
            vstr = vstr[:MAX_STR_LEN - 3] + '...'
        return TAG_TPL.format(code=tag.code, value=escape(vstr), type=escape(type_str))

    def marker(tag: DXFTag, tag_html: str) -> str:
        if tag.code == 0:
            return CONTROL_TPL.format(tag=tag_html)
        elif tag.code in GROUP_MARKERS:
            return MARKER_TPL.format(tag=tag_html)
        else:
            return tag_html

    def tags2html(tags: Iterable[DXFTag]) -> str:
        return '\n'.join(marker(tag, tag2html(tag)) for tag in tags)

    def groups(tags: Iterable[DXFTag]) -> Iterable[str]:
        for group in group_tags(tags, splitcode=0):
            yield '<div class="dxf-tag-group">\n{content}\n</div>'.format(content=tags2html(group))

    def dxf_control_structures(tags: Iterable[DXFTag]) -> str:
        return '\n'.join(groups(tags))

    template = load_resource('rawpp.html')
    return template.format(
        name=filename + (' (bin)' if binary else ' (asc)'),
        css=load_resource('rawpp.css'),
        dxf_file=dxf_control_structures(tagger),
    )
