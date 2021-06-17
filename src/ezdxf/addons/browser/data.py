#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional, Dict, List, Tuple
from pathlib import Path

from ezdxf.lldxf.loader import SectionDict
from ezdxf.addons.browser.loader import load_section_dict
from ezdxf.lldxf.types import DXFVertex
from ezdxf.lldxf.tags import Tags

__all__ = ["DXFDocument", "get_row_from_line_number", "dxfstr"]


class DXFDocument:
    def __init__(self, sections: SectionDict = None):
        # Important: the section dict has to store the raw string tags
        # else an association of line numbers to entities is not possible.
        # Comment tags (999) are ignored, because the load_section_dict()
        # function can not handle and store comments.
        # Therefore comments causes error in the line number associations and
        # should be stripped off before processing for precise debugging of
        # DXF files.
        # TODO: ezdxf strip-comments FILE
        self.sections: SectionDict = dict()
        self.handle_index: Optional[HandleIndex] = None
        self.line_index: Optional[LineIndex] = None
        self.filename = ""
        if sections:
            self.update(sections)

    @property
    def filepath(self):
        return Path(self.filename)

    @property
    def max_line_number(self) -> int:
        if self.line_index:
            return self.line_index.max_line_number
        else:
            return 1

    def load(self, filename: str):
        self.filename = filename
        self.update(load_section_dict(filename))

    def update(self, sections: SectionDict):
        self.sections = sections
        self.handle_index = HandleIndex(self.sections)
        self.line_index = LineIndex(self.sections)

    def absolute_filepath(self):
        return self.filepath.absolute()

    def get_header_section(self):
        return self.sections.get("HEADER")

    def get_entity(self, handle: str) -> Optional[Tags]:
        if self.handle_index:
            return self.handle_index.get(handle)
        return None

    def get_line_number(self, entity: Tags) -> Optional[int]:
        if self.line_index:
            return self.line_index.get_start_line_for_entity(entity)
        return None

    def get_entity_at_line(self, number: int) -> Optional[Tags]:
        if self.line_index:
            return self.line_index.get_entity_at_line(number)
        return None

    def next_entity(self, entity: Tags) -> Optional[Tags]:
        return self.handle_index.next_entity(entity)

    def previous_entity(self, entity: Tags) -> Optional[Tags]:
        return self.handle_index.previous_entity(entity)


class HandleIndex:
    def __init__(self, sections: SectionDict):
        self._index = HandleIndex.build(sections)

    def get(self, handle: str):
        return self._index.get(handle.upper())

    @staticmethod
    def build(sections: SectionDict) -> Dict:
        entity_index = dict()
        for section in sections.values():
            for entity in section:
                try:
                    handle = entity.get_handle()
                    entity_index[handle.upper()] = entity
                except ValueError:
                    pass
        return entity_index

    def next_entity(self, entity: Tags) -> Tags:
        return_next = False
        for e in self._index.values():
            if return_next:
                return e
            if e is entity:
                return_next = True
        return entity

    def previous_entity(self, entity: Tags) -> Tags:
        prev = entity
        for e in self._index.values():
            if e is entity:
                return prev
            prev = e
        return entity


class LineIndex:
    def __init__(self, sections: SectionDict):
        # id, (start_line_number, entity tags)
        self._entity_index: Dict[
            int, Tuple[int, Tags]
        ] = LineIndex.build_entity_index(sections)

        # entity index of sorted (start_line_number, entity) tuples
        index = LineIndex.build_line_index(sections)
        self._line_index: List[Tuple[int, Tags]] = index
        self._max_line_number = 1
        if index:
            last_start_number, e = self._line_index[-1]
            self._max_line_number = last_start_number + len(e) * 2 - 1

    @property
    def max_line_number(self) -> int:
        return self._max_line_number

    @staticmethod
    def build_entity_index(sections: SectionDict) -> Dict:
        index: Dict[int, Tuple[int, Tags]] = dict()
        line_number = 1
        for section in sections.values():
            # the section dict contain raw string tags
            for entity in section:
                index[id(entity)] = line_number, entity
                line_number += len(entity) * 2  # group code, value
            line_number += 2  # for missing ENDSEC tag
        return index

    @staticmethod
    def build_line_index(sections: SectionDict) -> List:
        index: List[Tuple[int, Tags]] = list()
        start_line_number = 1
        for name, section in sections.items():
            # the section dict contain raw string tags
            for entity in section:
                index.append((start_line_number, entity))
                # add 2 lines for each tag: group code, value
                start_line_number += len(entity) * 2
            start_line_number += 2  # for missing ENDSEC tag
        index.sort()  # sort index by line number
        return index

    def get_start_line_for_entity(self, entity: Tags) -> Optional[int]:
        entry = self._entity_index.get(id(entity))
        if entry:
            return entry[0]
        return None

    def get_entity_at_line(self, number: int) -> Optional[Tags]:
        index = self._line_index
        if len(index) == 0:
            return None

        _, entity = index[0]  # first entity
        for start, e in index:
            if start > number:
                return entity
            entity = e
        return entity


def get_row_from_line_number(
    entity: Tags, start_line_number: int, select_line_number: int
) -> int:
    count = select_line_number - start_line_number
    lines = 0
    row = 0
    for tag in entity:
        if lines >= count:
            return row
        if isinstance(tag, DXFVertex):
            lines += len(tag.value) * 2
        else:
            lines += 2
        row += 1
    return row


def dxfstr(tags: Tags) -> str:
    return "".join(tag.dxfstr() for tag in tags)


class EntityHistory:
    def __init__(self):
        self._history: List[Tags] = list()
        self._index: int = 0

    def __len__(self):
        return len(self._history)

    @property
    def index(self):
        return self._index

    def append(self, entity: Tags):
        self._index = len(self._history)
        self._history.append(entity)

    def back(self) -> Optional[Tags]:
        entity = None
        if self._history:
            index = self._index - 1
            entity = self._history[index]
            self._index = max(0, index)
        return entity

    def forward(self) -> Tags:
        entity = None
        if self._history:
            self._index = min(len(self._history) - 1, self._index + 1)
            entity = self._history[self._index]
        return entity

    def clear(self):
        self._history.clear()
        self._index = 0

    def content(self) -> List[Tags]:
        return list(self._history)
