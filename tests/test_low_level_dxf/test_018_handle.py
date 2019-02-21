# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
from ezdxf.tools.handle import HandleGenerator


def test_next():
    handles = HandleGenerator('100')
    assert '100' == handles.next()


def test_next_function():
    handles = HandleGenerator('100')
    assert '100' == next(handles)


def test_seed():
    handles = HandleGenerator('200')
    handles.next()
    assert '201' == str(handles)


def test_reset():
    handles = HandleGenerator('200')
    handles.reset('300')
    assert '300' == str(handles)
