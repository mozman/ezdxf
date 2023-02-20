# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.tools.handle import HandleGenerator


def test_next():
    handles = HandleGenerator("100")
    assert "100" == handles.next()


def test_next_function():
    handles = HandleGenerator("100")
    assert "100" == next(handles)


def test_seed():
    handles = HandleGenerator("200")
    handles.next()
    assert "201" == str(handles)


def test_returns_not_zero():
    handles = HandleGenerator("0")
    assert handles.next() != "0"


def test_returns_not_negative():
    handles = HandleGenerator("-2")
    assert int(handles.next(), 16) > 0


def test_reset():
    handles = HandleGenerator("200")
    handles.reset("300")
    assert "300" == str(handles)


def test_init_and_reset_rejects_invalid_ints():
    with pytest.raises(ValueError):
        HandleGenerator("XXXX")
    handles = HandleGenerator()
    with pytest.raises(ValueError):
        handles.reset("xyz")


def test_copy_handle_generator():
    h0 = HandleGenerator("1")
    h1 = h0.copy()
    assert h0.next() == h1.next()
    h1.next()
    assert str(h0) != str(h1)


def test_copied_handle_generators_are_independent():
    h0 = HandleGenerator("1")
    h1 = h0.copy()
    h1.next()
    assert str(h0) != str(h1)
