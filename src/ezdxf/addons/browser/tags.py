# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.const import DXFStructureError


def compile_tags(tags: Tags) -> Tags:
    try:
        return Tags(tag_compiler(iter(tags)))
    except DXFStructureError:
        return tags
