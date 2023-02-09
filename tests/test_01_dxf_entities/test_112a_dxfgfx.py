# Copyright (c) 2019-2022 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities.dxfgfx import DXFGraphic, is_graphic_entity
from ezdxf.math import Matrix44
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.entities.dxfns import recover_graphic_attributes
from ezdxf.lldxf.const import DXFValueError


@pytest.fixture
def entity():
    return DXFGraphic.from_text(LINE)


def test_is_graphic_entity(entity):
    assert is_graphic_entity(entity) is True


def test_init_from_tags(entity):
    assert entity.dxf.layer == "Layer"


def test_true_color(entity):
    entity.dxf.true_color = 0x0F0F0F
    assert 0x0F0F0F == entity.dxf.true_color
    assert (
        0x0F,
        0x0F,
        0x0F,
    ) == entity.rgb  # shortcut for modern graphic entities
    entity.rgb = (255, 255, 255)  # shortcut for modern graphic entities
    assert 0xFFFFFF == entity.dxf.true_color


def test_color_name(entity):
    entity.dxf.color_name = "Rot"
    assert "Rot" == entity.dxf.color_name


def test_transparency(entity):
    entity.dxf.transparency = (
        0x020000FF  # 0xFF = opaque; 0x00 = 100% transparent
    )
    assert 0x020000FF == entity.dxf.transparency
    # recommend usage: helper property ModernGraphicEntity.transparency
    assert 0.0 == entity.transparency  # 0. =  opaque; 1. = 100% transparent
    entity.transparency = 1.0
    assert 0x02000000 == entity.dxf.transparency


def test_default_attributes():
    entity = DXFGraphic.new()
    assert entity.dxf.layer == "0"
    assert entity.dxf.hasattr("layer") is True, "real attribute required"
    assert entity.dxf.color == 256
    assert entity.dxf.hasattr("color") is False, "just the default value"
    assert entity.dxf.linetype == "BYLAYER"
    assert entity.dxf.hasattr("linetype") is False, "just the default value"


def test_aci_color_index_fixer(entity):
    entity.dxf.color = -1
    assert entity.dxf.color == 256  # fixed as BYLAYER
    entity.dxf.color = 258
    assert entity.dxf.color == 256  # fixed as BYLAYER


def test_lineweight_fixer(entity):
    entity.dxf.lineweight = -5
    assert entity.dxf.lineweight == -1  # fixed as BYLAYER
    entity.dxf.lineweight = 17
    assert entity.dxf.lineweight == 18  # fixed as nearest valid lineweight
    entity.dxf.lineweight = 255
    assert entity.dxf.lineweight == 211  # fixed as nearest valid lineweight


def test_is_linetype_validator_active(entity):
    with pytest.raises(DXFValueError):
        entity.dxf.linetype = "*Invalid"


def test_is_layer_name_validator_active(entity):
    with pytest.raises(DXFValueError):
        entity.dxf.layer = "*Invalid"


def test_clone_graphical_entity(entity):
    entity.dxf.handle = "EFEF"
    entity.dxf.owner = "ABBA"
    entity.dxf.layer = "Layer1"
    entity.dxf.color = 13
    entity.set_reactors(["A", "F"])
    entity.set_xdata("MOZMAN", [(1000, "extended data")])

    clone = entity.copy()
    assert clone.dxf is not entity.dxf, "should be different objects"
    assert clone.dxf.handle is None, "should not have a handle"
    assert clone.dxf.owner is None
    assert clone.dxf.layer == "Layer1"
    assert clone.dxf.color == 13
    assert clone.reactors is not entity.reactors, "should be different objects"
    assert len(clone.get_reactors()) == 0
    assert clone.xdata is not entity.xdata, "should be different objects"
    assert clone.get_xdata("MOZMAN") == [(1000, "extended data")]

    clone.dxf.handle = "CDCD"
    clone.dxf.owner = "FEFE"
    clone.dxf.layer = "Layer2"
    clone.dxf.color = 77
    clone.set_reactors([])
    clone.set_xdata("MOZMAN", [(1000, "extended data1")])

    # don't change source entity
    assert entity.dxf.handle == "EFEF"
    assert entity.dxf.owner == "ABBA"
    assert entity.dxf.layer == "Layer1"
    assert entity.dxf.color == 13
    assert entity.get_reactors() == ["A", "F"]
    assert entity.get_xdata("MOZMAN") == [(1000, "extended data")]


def test_basic_transformation_interfaces():
    # test basic implementation = forward operation to transform interface
    class BasicGraphic(DXFGraphic):
        def transform(self, m: Matrix44) -> DXFGraphic:
            return self

    interface_mockup = BasicGraphic.new()
    assert interface_mockup.translate(1, 2, 3) is interface_mockup
    assert interface_mockup.scale(1, 2, 3) is interface_mockup
    assert interface_mockup.scale_uniform(1) is interface_mockup
    assert interface_mockup.rotate_axis((1, 2, 3), 1) is interface_mockup
    assert interface_mockup.rotate_x(1) is interface_mockup
    assert interface_mockup.rotate_y(1) is interface_mockup
    assert interface_mockup.rotate_z(1) is interface_mockup


def test_unlink_from_layout(entity):
    doc = ezdxf.new()
    msp = doc.modelspace()
    point = msp.add_point((0, 0))
    assert point.dxf.owner is not None
    point.unlink_from_layout()
    assert point.dxf.owner is None
    assert (
        point.dxf.handle in doc.entitydb
    ), "Do not delete unlinked entity from entitydb."

    # unlinking an already unlinked entity should pass silently
    point.unlink_from_layout()


def test_unlink_from_layout_without_doc(entity):
    entity.unlink_from_layout()
    assert entity.dxf.owner is None


def test_unlink_destroyed_entity_from_layout(entity):
    entity.destroy()
    with pytest.raises(TypeError):
        entity.unlink_from_layout()


def test_recover_acdb_entity_tags():
    entity = DXFGraphic()
    tags = Tags([DXFTag(62, 1), DXFTag(8, "Layer"), DXFTag(6, "Linetype")])

    recover_graphic_attributes(tags, entity.dxf)
    assert entity.dxf.color == 1
    assert entity.dxf.layer == "Layer"
    assert entity.dxf.linetype == "Linetype"


def test_recover_acdb_entity_tags_does_not_replace_existing_attribs():
    entity = DXFGraphic()
    entity.dxf.color = 7
    entity.dxf.layer = "HasLayer"
    entity.dxf.linetype = "HasLinetype"
    tags = Tags([DXFTag(62, 1), DXFTag(8, "Layer"), DXFTag(6, "Linetype")])

    recover_graphic_attributes(tags, entity.dxf)
    assert entity.dxf.color == 7
    assert entity.dxf.layer == "HasLayer"
    assert entity.dxf.linetype == "HasLinetype"


def test_recover_acdb_entity_tags_ignores_unknown_tags():
    entity = DXFGraphic()
    tags = Tags([DXFTag(62, 1), DXFTag(8, "Layer"), DXFTag(99, "Unknown")])

    unprocessed_tags = recover_graphic_attributes(tags, entity.dxf)
    assert len(unprocessed_tags) == 1
    assert unprocessed_tags[0] == (99, "Unknown")


LINE = """0
LINE
5
0
330
0
100
AcDbEntity
8
Layer
6
Linetype
62
77
370
25
100
AcDbLine
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""
