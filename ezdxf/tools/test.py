# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.lldxf.tagger import internal_tag_compiler
from ..modern import ModernDXFFactory


def compile_tags_without_handles(text):
    return (tag for tag in internal_tag_compiler(text) if tag.code not in (5, 105))


def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]


def load_section(text, name, database=None, dxffactory=None):
    from ezdxf.lldxf.loader import load_dxf_structure, fill_database
    dxf = load_dxf_structure(internal_tag_compiler(text), ignore_missing_eof=True)
    if database is not None:
        fill_database(database, dxf, dxffactory)
    return dxf[name]


SUPPORTED_ENTITIES = ModernDXFFactory(None).ENTITY_WRAPPERS
def find_unsupported_entities(container):
    unsupported_entities = set()
    for entity in container:
        dxftype = entity.dxftype()
        if dxftype not in SUPPORTED_ENTITIES:
            unsupported_entities.add(dxftype)
    return unsupported_entities

