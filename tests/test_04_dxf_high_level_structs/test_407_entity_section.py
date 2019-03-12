# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
#
# The entities section is a virtual construct while working on a document.
# In reality it is a section in the DXF file containing the entities of the modelspace and the active paperspace, other
# layouts are stored in the associated BLOCK in the blocks section. I assume this is just a legacy detail, which could
# easily removed by storing all layouts including the modelspace in the block sections.
#
# In later ezdxf versions the EntitiesSection object has only the task to load and store the entities of the DXF section
# ENTITIES.
#
import ezdxf


def test_iterate_entities_section():
    doc = ezdxf.new()
    m = doc.modelspace()
    m.add_line((0, 0), (1, 1))
    entity = list(doc.entities)[-1]
    assert doc == entity.doc  # check drawing attribute
