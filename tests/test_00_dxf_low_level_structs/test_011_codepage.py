# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
from ezdxf.tools.codepage import toencoding, tocodepage


def test_ansi_1250():
    assert "cp1250" == toencoding("ansi_1250")


def test_default():
    assert "cp1252" == toencoding("xyz")


def test_tocodepage_1252():
    assert "ANSI_1252" == tocodepage("cp1252")


def test_tocodepage_936():
    assert "ANSI_936" == tocodepage("gbk")
