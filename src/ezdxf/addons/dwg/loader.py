# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from ezdxf.lldxf.loader import SectionDict
from ezdxf.drawing import Drawing


def readfile(filename: str) -> 'Drawing':
    data = open(filename, 'rb').read()
    return load(data)


def load(data: bytes) -> Drawing:
    sections = load_section_dict(data)
    return Drawing.from_section_dict(sections)


def load_section_dict(data: bytes) -> SectionDict:
    pass
