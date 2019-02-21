# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.database import EntityDB
from ezdxf.entityspace import EntitySpace
from ezdxf.lldxf.tags import internal_tag_compiler, group_tags


@pytest.fixture
def space():
    return EntitySpace(EntityDB())


def test_add_to_entity_space(space):
    for group in group_tags(internal_tag_compiler(TESTENTITIES)):
        space.store_tags(group)
    assert 4 == len(space)


TESTENTITIES = """  0
POLYLINE
  5
239
  8
0
  6
BYBLOCK
 62
     0
 66
     1
 10
0.0
 20
0.0
 30
0.0
 40
0.15
 41
0.15
  0
VERTEX
  5
403
  8
0
  6
BYBLOCK
 62
     0
 10
-0.5
 20
-0.5
 30
0.0
  0
VERTEX
  5
404
  8
0
  6
BYBLOCK
 62
     0
 10
0.5
 20
0.5
 30
0.0
  0
SEQEND
  5
405
  8
0
  6
BYBLOCK
 62
     0
"""
