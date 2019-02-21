# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf


def test_tables_are_iterable():
    doc = ezdxf.new2()
    assert sum(len(list(table)) for table in doc.sections.tables) > 10

