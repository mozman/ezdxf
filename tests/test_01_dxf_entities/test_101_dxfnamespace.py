# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import pytest
from copy import deepcopy
from ezdxf.math import Vec3
from ezdxf.entities.dxfentity import (
    base_class,
    DXFAttributes,
    DXFNamespace,
    SubclassProcessor,
)
from ezdxf.lldxf.attributes import (
    group_code_mapping,
    DefSubclass,
    DXFAttr,
    XType,
)
from ezdxf.entities.dxfgfx import acdb_entity
from ezdxf.entities.line import acdb_line
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.const import DXFAttributeError
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.lldxf.tags import Tags, DXFTag


class DXFEntity:
    """Mockup"""

    DXFTYPE = "DXFENTITY"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_line)


@pytest.fixture
def entity():
    return DXFEntity()


@pytest.fixture
def processor():
    return SubclassProcessor(ExtendedTags.from_text(TEST_1))


def test_handle_and_owner(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.handle == "FFFF"
    assert attribs.owner == "ABBA"
    assert attribs._entity is entity


def test_default_values(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.layer == "0"
    assert attribs.color == 256
    assert attribs.linetype == "BYLAYER"
    # this attributes do not really exist
    assert attribs.hasattr("layer") is False
    assert attribs.hasattr("color") is False
    assert attribs.hasattr("linetype") is False


def test_get_value_with_default(entity, processor):
    attribs = DXFNamespace(processor, entity)
    # return existing values
    assert attribs.get("handle", "0") == "FFFF"
    # return given default value not DXF default value, which would be '0'
    assert attribs.get("layer", "mozman") == "mozman"
    # attribute has to a valid DXF attribute
    with pytest.raises(DXFAttributeError):
        _ = attribs.get("hallo", 0)

    # attribs without default returns None -> will not exported to DXF file
    assert attribs.color_name is None


def test_set_values(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.handle = "CDEF"
    assert attribs.handle == "CDEF"
    attribs.set("owner", "DADA")
    assert attribs.owner == "DADA"
    # set new attribute
    attribs.color = 7
    assert attribs.color == 7
    attribs.set("linetype", "DOT")
    assert attribs.linetype == "DOT"
    # attribute has to a valid DXF attribute
    with pytest.raises(DXFAttributeError):
        attribs.hallo = 0
    with pytest.raises(DXFAttributeError):
        attribs.set("hallo", 0)


def test_value_types(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.handle = (
        None  # None is always accepted, attribute is ignored at export
    )
    assert attribs.handle is None
    attribs.handle = "XYZ"
    assert attribs.handle == "XYZ", "handle is just a string"
    attribs.handle = 123
    assert attribs.handle == "123", "handle is just a string"
    with pytest.raises(ValueError):
        attribs.color = "xxx"

    attribs.start = (1, 2, 3)  # type: Vec3
    assert attribs.start == (1, 2, 3)
    assert attribs.start.x == 1
    assert attribs.start.y == 2
    assert attribs.start.z == 3


def test_delete_attribs(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.layer = "mozman"
    assert attribs.layer == "mozman"
    del attribs.layer

    # default value
    assert attribs.layer == "0"
    with pytest.raises(DXFAttributeError):
        del attribs.color
    attribs.discard("color")  # delete silently if not exist
    with pytest.raises(DXFAttributeError):
        del attribs.unsupported_attribute


def test_is_supported(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.is_supported("linetype") is True
    assert (
        attribs.is_supported("true_color") is True
    )  # ezdxf does not care about DXF versions at runtime
    assert attribs.is_supported("xxx_mozman_xxx") is False


def test_dxftype(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.dxftype == "DXFENTITY"


def test_cloning(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.color = 77
    attribs2 = attribs.copy(entity)
    # clone everything
    assert attribs2._entity is attribs._entity
    assert attribs2.handle is attribs.handle
    assert attribs2.owner is attribs.owner
    assert attribs2.color == 77
    # do not harm original entity
    assert attribs._entity is entity
    assert attribs.handle == "FFFF"
    assert attribs.owner == "ABBA"
    # change clone
    attribs2.color = 13
    assert attribs.color == 77
    assert attribs2.color == 13


def test_deepcopy_usage(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.color = 77

    attribs2 = deepcopy(attribs)
    # clone everything
    assert attribs2._entity is attribs._entity
    assert attribs2.handle is attribs.handle
    assert attribs2.owner is attribs.owner
    assert attribs2.color == 77
    # do not harm original entity
    assert attribs._entity is entity
    assert attribs.handle == "FFFF"
    assert attribs.owner == "ABBA"
    # change clone
    attribs2.color = 13
    assert attribs.color == 77
    assert attribs2.color == 13


def test_dxf_export_one_attribute(entity, processor):
    attribs = DXFNamespace(processor, entity)
    tagwriter = TagCollector()
    attribs.export_dxf_attribs(tagwriter, "handle")
    assert len(tagwriter.tags) == 1
    assert tagwriter.tags[0] == (5, "FFFF")
    with pytest.raises(DXFAttributeError):
        attribs.export_dxf_attribute(tagwriter, "mozman")


def test_dxf_export_two_attribute(entity, processor):
    attribs = DXFNamespace(processor, entity)
    tagwriter = TagCollector()
    attribs.export_dxf_attribs(tagwriter, ["handle", "owner"])
    assert len(tagwriter.tags) == 2
    assert tagwriter.tags[0] == (5, "FFFF")
    assert tagwriter.tags[1] == (330, "ABBA")


class TestUpdateDXFAttributes:
    """Tests for DXFNamespace.update()"""

    @pytest.fixture
    def dxf(self, processor, entity):
        ns = DXFNamespace(processor, entity)
        ns.color = 7
        ns.handle = "ABBA"
        ns.owner = "FEFE"
        return ns

    def test_regular_usage(self, dxf):
        dxf.update({"color": 1})
        assert dxf.color == 1

    def test_protect_entity_back_link_from_update(self, dxf):
        entity = dxf._entity
        dxf.update({"_entity": None})
        assert entity is dxf._entity

    def test_protect_handle_and_owner_from_update_by_default(self, dxf):
        dxf.update({"handle": "BAAB", "owner": "DEDE"})
        assert dxf.handle == "ABBA"
        assert dxf.owner == "FEFE"

    def test_can_exclude_attributes_from_update(self, dxf):
        entity = dxf._entity
        dxf.update({"color": 1, "_entity": None}, exclude={"color"})
        assert dxf.color == 7
        assert (
            dxf._entity is entity
        ), "entity back-link has to be protected from update"

    def test_can_update_handle_and_owner_on_demand(self, dxf):
        entity = dxf._entity
        # do not include "handle" and "owner" in custom exclude set:
        exclude = set()
        dxf.update(
            {"handle": "BAAB", "owner": "DEDE", "_entity": None},
            exclude=exclude,
        )
        assert dxf.handle == "BAAB"
        assert dxf.owner == "DEDE"
        assert (
            dxf._entity is entity
        ), "entity back-link always has to be protected from update"

    def test_raises_attribute_error_for_invalid_attribute(self, dxf):
        with pytest.raises(AttributeError):
            dxf.update({"xxx": "yyy"})

    def test_raises_value_error_for_invalid_attribute_value(self, dxf):
        with pytest.raises(ValueError):
            dxf.update({"color": "yyy"})

    def test_update_can_ignore_errors_on_demand(self, dxf):
        dxf.update({"xxx": "yyy", "color": "zzz"}, ignore_errors=True)
        assert dxf.hasattr("xxx") is False
        assert dxf.color == 7


@pytest.fixture
def subclass():
    return DefSubclass(
        "AcDbTest",
        {
            "test1": DXFAttr(1),
            "test2": DXFAttr(2),
            "test3": DXFAttr(1),  # duplicate group code
            "callback": DXFAttr(3, xtype=XType.callback),
            "none_callback": DXFAttr(3),  # duplicate group code
        },
    )


@pytest.fixture
def cls(subclass):
    class TestEntity(DXFEntity):
        DXFATTRIBS = DXFAttributes(subclass)

    return TestEntity


def load_tags_fast(cls, subclass, data):
    ns = DXFNamespace(entity=cls())
    mapping = group_code_mapping(subclass)
    proc = SubclassProcessor(ExtendedTags(tags=data))
    unprocessed_tags = proc.fast_load_dxfattribs(ns, mapping, 0)
    return ns, unprocessed_tags


def test_if_fast_load_handles_duplicate_group_codes(cls, subclass):
    data = Tags(
        [
            DXFTag(0, "ENTITY"),  # First subclass tag should be ignored
            DXFTag(1, "1"),  # duplicate group code
            DXFTag(2, "2"),
            DXFTag(1, "3"),  # duplicate group code
            DXFTag(7, "unprocessed tag"),
        ]
    )
    ns, unprocessed_tags = load_tags_fast(cls, subclass, data)
    assert ns.test1 == "1"
    assert ns.test2 == "2"
    assert ns.test3 == "3"
    assert len(unprocessed_tags) == 1
    assert unprocessed_tags[0] == (7, "unprocessed tag")


def test_if_fast_load_handles_callback_group_codes(cls, subclass):
    data = Tags(
        [
            DXFTag(0, "ENTITY"),  # First subclass tag should be ignored
            DXFTag(3, "X"),  # callback value
            DXFTag(3, "Y"),  # none callback value
        ]
    )
    ns, unprocessed_tags = load_tags_fast(cls, subclass, data)
    assert ns.none_callback == "Y"
    assert ns.hasattr("callback") is False


def test_if_fast_load_handles_unprocessed_duplicate_group_codes(cls, subclass):
    data = Tags(
        [
            DXFTag(0, "ENTITY"),  # First subclass tag should be ignored
            DXFTag(1, "1"),  # duplicate group code
            DXFTag(1, "3"),  # duplicate group code
            DXFTag(
                1, "5"
            ),  # duplicate group code, but without an attribute definition
        ]
    )
    ns, unprocessed_tags = load_tags_fast(cls, subclass, data)
    assert ns.test1 == "1"
    assert ns.test3 == "3"
    # only two group code 1 attributes are defined:
    assert len(unprocessed_tags) == 1
    assert unprocessed_tags[0] == (1, "5")


def test_detect_implementation_version_returns_stored_version():
    processor = SubclassProcessor(
        ExtendedTags.from_text(GEODATA_V1), dxfversion="AC1015"
    )
    assert (
        processor.detect_implementation_version(
            subclass_index=1, group_code=90, default=2
        )
        == 1
    )


def test_detect_implementation_version_returns_default():
    processor = SubclassProcessor(
        ExtendedTags.from_text(TEST_1), dxfversion="AC1015"
    )
    assert (
        processor.detect_implementation_version(
            subclass_index=1, group_code=90, default=2
        )
        == 2
    )


TEST_1 = """0
DXFENTITY
5
FFFF
330
ABBA
"""

GEODATA_V1 = """0
GEODATA
5
395
330
1C5
100
AcDbGeoData
90
1
70
0
"""
if __name__ == "__main__":
    pytest.main([__file__])
