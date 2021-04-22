#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List, Dict, Iterable
from .mtext import MText, MTextColumns

__all__ = ["make_static_columns", "make_static_columns_r2018"]

COLUMN_BREAK = "\\N"


def add_column_breaks(content: Iterable[str]) -> Iterable[str]:
    for c in content:
        if not c.endswith(COLUMN_BREAK):
            c += COLUMN_BREAK
        yield c


def make_static_columns(
        content: List[str], width: float, gutter_width: float, height: float,
        dxfattribs: Dict = None) -> MText:
    if len(content) < 1:
        raise ValueError("no content")
    columns = MTextColumns.new_static_columns(
        len(content), width, gutter_width, height)
    mtext = MText.new(dxfattribs=dxfattribs)
    mtext.setup_columns(columns, linked=True)
    content = list(add_column_breaks(content))
    mtext.text = content[0]
    for mt, c in zip(mtext.columns.linked_columns, content[1:]):
        mt.text = c
    return mtext


def make_static_columns_r2018(
        content: List[str], width: float, gutter_width: float, height: float,
        dxfattribs: Dict = None) -> MText:
    if len(content) < 1:
        raise ValueError("no content")
    columns = MTextColumns.new_static_columns(
        len(content), width, gutter_width, height)
    mtext = MText.new(dxfattribs=dxfattribs)
    mtext.setup_columns(columns, linked=False)
    mtext.text = ''.join(add_column_breaks(content))
    return mtext
