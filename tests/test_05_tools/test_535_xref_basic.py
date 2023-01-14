#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf import xref, colors, const
from ezdxf.document import Drawing
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.render.arrows import ARROWS
from ezdxf.entities import Polyline, Polyface, factory, Insert


def forward_handles(doc, count: int) -> None:
    for _ in range(count):
        doc.entitydb.next_handle()


class TestLoadResourcesWithoutNamingConflicts:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.layers.add("FIRST")
        doc.linetypes.add(  # see also: complex_line_type_example.py
            "SQUARE",
            pattern="A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
            description="Square -[]-----[]-----[]-----[]----[]----",
            length=1.45,
        )
        doc.linetypes.add(
            "GAS",
            pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
            description="Gas ----GAS----GAS----GAS----GAS----GAS----GAS--",
            length=1,
        )
        arial = doc.styles.add("ARIAL", font="Arial.ttf")
        arial.set_extended_font_data(family="Arial", italic=False, bold=True)
        doc.layers.add("SECOND", linetype="SQUARE")
        dimstyle = setup_dimstyle(
            doc, "EZ_M_100_H25_CM", style="ARIAL", name="TestDimStyle"
        )
        dimstyle.dxf.dimltype = "GAS"
        dimstyle.dxf.dimblk = ARROWS.dot

        material = doc.materials.new("ExoticBlue")
        material.dxf.ambient_color_value = colors.encode_raw_color((0, 0, 255))
        layer = doc.layers.add("Layer_with_material")
        layer.dxf.material_handle = material.dxf.handle
        return doc

    def test_loading_a_simple_layer(self, sdoc):
        """This is the basic test to load a simple entity like a layer into a new
        document. It is checked whether all required structures have been created.
        """
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["first"])
        loader.execute()
        layer = tdoc.layers.get("first")

        assert layer is not sdoc.layers.get("first"), "expected a copy"
        assert layer.dxf.name == "FIRST", "expected the original layer name"
        assert layer.doc is tdoc, "bound to wrong document"
        assert layer.dxf.handle in tdoc.entitydb, "entity not in database"
        assert layer.dxf.owner == tdoc.layers.head.dxf.handle, "invalid owner handle"
        assert layer.dxf.material_handle == tdoc.materials["global"].dxf.handle

    def test_loading_a_shape_linetype(self, sdoc):
        """Load a complex linetype with shapes which requires to load the dependent
        shape-file entry too.
        """
        tdoc = ezdxf.new()
        # handles shouldn't be synchronized to the source document!
        forward_handles(tdoc, 7)
        assert (
            sdoc.styles.find_shx("ltypeshp.shx").dxf.font == "ltypeshp.shx"
        ), "expected ltypeshp.shx entry to exist in the source document"

        loader = xref.Loader(sdoc, tdoc)
        loader.load_linetypes(["square"])
        loader.execute()
        ltype = tdoc.linetypes.get("square")
        assert ltype.dxf.name == "SQUARE"
        # do not repeat more tests from test_loading_a_simple_layer()

        style = tdoc.styles.find_shx("ltypeshp.shx")
        assert style.dxf.font == "ltypeshp.shx"
        pattern_style_handle = ltype.pattern_tags.get_style_handle()
        assert pattern_style_handle != "0"
        assert (
            pattern_style_handle == style.dxf.handle
        ), "expected handle of shape-file 'ltypeshp.shx' as pattern style handle"

    def test_loading_a_text_linetype(self, sdoc):
        """Load a complex linetype which contains text, the handle to the text style
        should point to the STANDARD text style in the target document.
        """
        tdoc = ezdxf.new()
        # handles shouldn't be synchronized to the source document!
        forward_handles(tdoc, 11)
        loader = xref.Loader(sdoc, tdoc)
        loader.load_linetypes(["gas"])
        loader.execute()
        ltype = tdoc.linetypes.get("gas")
        assert ltype.dxf.name == "GAS"
        # do not repeat more tests from test_loading_a_simple_layer()

        style = tdoc.styles.get("STANDARD")
        pattern_style_handle = ltype.pattern_tags.get_style_handle()
        assert pattern_style_handle != "0"
        assert (
            pattern_style_handle == style.dxf.handle
        ), "expected handle of text style STANDARD as pattern style handle"

    def test_loading_layer_with_complex_linetype(self, sdoc):
        """Loading a layer which references a complex linetype that also requires
        loading of an additional text style.
        """
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["second"])
        loader.execute()
        layer = tdoc.layers.get("second")
        assert layer.dxf.name == "SECOND", "expected the original layer name"

        # Test if required resources are loaded:
        ltype = tdoc.linetypes.get(layer.dxf.linetype)
        assert ltype.dxf.name == "SQUARE", "expected linetype SQUARE in target doc"
        assert tdoc.styles.find_shx("ltypeshp.shx") is not None

    def test_loading_a_text_style_with_extended_font_data(self, sdoc):
        """The extended font data is stored into XDATA section of the STYLE table entry."""
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_text_styles(["arial"])
        loader.execute()
        arial = tdoc.styles.get("arial")
        assert arial.dxf.name == "ARIAL", "expected text style ARIAL in target doc"

        family, italic, bold = arial.get_extended_font_data()
        assert family == "Arial"
        assert italic is False
        assert bold is True

    def test_loading_dimstyle(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_dim_styles(["TestDimStyle"])
        loader.execute()

        dimstyle = tdoc.dimstyles.get("TestDimStyle")
        assert dimstyle.dxf.name == "TestDimStyle"

        assert dimstyle.dxf.dimtxsty == "ARIAL"
        arial = tdoc.styles.get("arial")
        assert arial.dxf.name == "ARIAL", "expected text style ARIAL in target doc"

        assert dimstyle.dxf.dimltype == "GAS"
        ltype = tdoc.linetypes.get("GAS")
        assert ltype.dxf.name == "GAS", "expected linetype GAS in target doc"

        assert dimstyle.dxf.dimblk == ARROWS.dot
        # Note: ACAD arrow head blocks are created automatically at export in
        # DimStyle.set_blk_handle() if they do not exist

    def test_loading_layer_with_custom_default_material(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_layers(["Layer_with_material"])
        loader.execute()

        assert (
            "ExoticBlue" in tdoc.materials
        ), "expected copied entry in MATERIAL collection in target doc"
        layer = tdoc.layers.get("Layer_with_material")
        handle = layer.dxf.material_handle
        material = tdoc.entitydb.get(handle)
        assert material.dxf.name == "ExoticBlue"
        ambient_color = material.dxf.ambient_color_value
        assert colors.decode_raw_color(ambient_color)[1] == (0, 0, 255)


class TestLoadEntities:
    @pytest.fixture
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.layers.add("Layer0")
        doc.linetypes.add("LType0", [0.0])  # CONTINUOUS
        doc.appids.add("TEST_ID")
        return doc

    def test_load_plain_entity(self, sdoc):
        msp = sdoc.modelspace()
        msp.add_point((0, 0), dxfattribs={"layer": "Layer0", "linetype": "LType0"})

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert tdoc.layers.has_entry("Layer0") is True
        assert tdoc.linetypes.has_entry("LType0") is True

        target_msp = tdoc.modelspace()
        assert len(target_msp) == 1
        point = target_msp[0]
        assert point.doc is tdoc, "wrong document assigment"
        assert point.dxf.owner == target_msp.block_record_handle, "wrong owner handle"
        assert point.dxf.layer == "Layer0", "layer attribute not copied"

    def test_load_entity_with_xdata(self, sdoc):
        msp = sdoc.modelspace()
        point0 = msp.add_point((0, 0), dxfattribs={"layer": "Layer0"})
        point1 = msp.add_point((0, 0), dxfattribs={"layer": "Layer0"})
        point0.set_xdata(
            "TEST_ID",
            [
                (1000, "some text"),
                (1005, point1.dxf.handle),
                (1005, "FEFE"),  # FEFE to nothing and should be replaced by handle "0"
            ],
        )

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert tdoc.appids.has_entry("TEST_ID")
        tp0, tp1 = tdoc.modelspace()
        assert tp0.xdata is not None
        xdata = tp0.get_xdata("TEST_ID")
        assert xdata[0] == (1000, "some text")
        assert xdata[1] == (
            1005,
            tp1.dxf.handle,
        ), "expected handle of point1 to be mapped"
        assert xdata[2] == (
            1005,
            "0",
        ), "expected un-mappable handle to be 0"

    def test_load_entity_with_reactors(self, sdoc):
        msp = sdoc.modelspace()
        point0 = msp.add_point((0, 0), dxfattribs={"layer": "Layer0"})
        point1 = msp.add_point((0, 0), dxfattribs={"layer": "Layer0"})
        point0.set_reactors([point1.dxf.handle, "FEFE"])

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        tp0, tp1 = tdoc.modelspace()
        reactors = tp0.reactors.get()
        assert len(reactors) == 1
        assert reactors[0] == tp1.dxf.handle

    def test_load_entity_with_extension_dict(self, sdoc):
        msp = sdoc.modelspace()
        point0 = msp.add_point((0, 0), dxfattribs={"layer": "Layer0"})
        xdict = point0.new_extension_dict()
        xdict.add_dictionary_var("Test0", "Content0")

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        copy = tdoc.modelspace()[0]
        assert copy.has_extension_dict is True
        xdict = copy.get_extension_dict()
        assert xdict.dictionary.doc is tdoc
        assert (xdict.dictionary in tdoc.objects) is True

        dict_var = xdict["Test0"]
        assert dict_var.dxf.value == "Content0"
        assert (dict_var in tdoc.objects) is True


class TestLoadTextEntities:
    @pytest.fixture
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.styles.add("ARIAL", font="Arial.ttf")
        return doc

    def test_load_text_entity(self, sdoc):
        msp = sdoc.modelspace()
        msp.add_text("MyText", dxfattribs={"style": "ARIAL"})
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert tdoc.styles.has_entry("ARIAL")

    def test_load_mtext_entity(self, sdoc):
        msp = sdoc.modelspace()
        msp.add_mtext("MyText", dxfattribs={"style": "ARIAL"})
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert tdoc.styles.has_entry("ARIAL")

    def test_attdef_with_embedded_mtext_entity(self, sdoc):
        msp = sdoc.modelspace()
        attdef = msp.add_attdef("TEST", insert=(0, 0))
        mtext = msp.add_mtext("TEST", dxfattribs={"style": "ARIAL"})
        attdef.embed_mtext(mtext)
        # hack: embed_mtext() copies the style of the mtext into attdef
        # this may not always be true for loaded entities:
        attdef.dxf.style = "Standard"

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert tdoc.styles.has_entry("ARIAL") is True


def test_load_mtext_with_columns():
    sdoc = ezdxf.new("R2000")
    sdoc.styles.add("ARIAL1", font="Arial.ttf")
    sdoc.styles.add("ARIAL2", font="Arial.ttf")
    mtext = sdoc.modelspace().add_mtext_static_columns(
        ["mtext0", "column1", "column2"],
        width=5,
        gutter_width=1,
        height=5,
        dxfattribs={"style": "ARIAL1"},
    )
    mtext.columns.linked_columns[1].dxf.style = "ARIAL2"

    tdoc = ezdxf.new("R2000")
    xref.load_modelspace(sdoc, tdoc)
    assert tdoc.styles.has_entry("ARIAL1")
    assert tdoc.styles.has_entry("ARIAL2")

    loaded_mtext = tdoc.modelspace()[0]
    assert loaded_mtext.has_columns is True
    columns = loaded_mtext.columns.linked_columns
    assert len(columns) == 2
    assert all(
        factory.is_bound(column, tdoc) for column in columns
    ), "all columns (MTEXT) should be bound to tdoc"


class TestLoadLinkedEntities:
    @pytest.fixture
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.layers.add("Layer0")
        doc.linetypes.add("LType0", [0.0])  # CONTINUOUS
        return doc

    def test_load_polyline(self, sdoc):
        polyline = sdoc.modelspace().add_polyline2d([(0, 0), (1, 0), (1, 1)])
        polyline.vertices[0].dxf.linetype = "LType0"
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert tdoc.linetypes.has_entry("LType0")
        loaded_polyline = cast(Polyline, tdoc.modelspace()[0])
        assert isinstance(loaded_polyline, Polyline)
        assert len(loaded_polyline.vertices) == 3
        assert all(
            factory.is_bound(v, tdoc) for v in loaded_polyline.vertices
        ), "all vertices should be bound to tdoc"
        assert all(
            v.dxf.owner == loaded_polyline.dxf.owner for v in loaded_polyline.vertices
        ), "all vertices should have the same owner as POLYLINE"
        assert (
            loaded_polyline.seqend.dxf.owner == loaded_polyline.dxf.owner
        ), "SEQEND owner should be the POLYLINE owner"

    def test_load_polyface(self, sdoc):
        polyface = sdoc.modelspace().add_polyface()
        polyface.append_face([(0, 0), (1, 0), (1, 1)])
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        loaded_polyface = cast(Polyface, tdoc.modelspace()[0])
        assert isinstance(loaded_polyface, Polyface)
        faces = list(loaded_polyface.faces())
        assert len(faces[0]) == 3 + 1  # vertices + face-record
        assert all(factory.is_bound(v, tdoc) for v in loaded_polyface.vertices)


class TestBlocks:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.layers.add("Layer0")
        doc.linetypes.add("LType0", [0.0])  # CONTINUOUS
        block = doc.blocks.new("TestBlock")
        block.add_line(
            (0, 0), (1, 1), dxfattribs={"linetype": "LType0", "layer": "Layer0"}
        )
        block_ref = doc.modelspace().add_blockref("TestBlock", insert=(0, 0))
        block_ref.add_attrib("TestTag", "Content")
        return doc

    def test_load_block_layout(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)
        loader.load_block_layout(sdoc.blocks.get("TestBlock"))
        loader.execute()

        assert tdoc.layers.has_entry("Layer0"), "expected loaded LAYER"
        assert tdoc.linetypes.has_entry("LType0"), "expected loaded LTYPE"
        assert tdoc.block_records.has_entry("TestBlock"), "expected loaded BLOCK_RECORD"

        loaded_block = tdoc.blocks.get("TestBlock")
        assert loaded_block is not None, "loaded BlockLayout does not exist"
        assert len(loaded_block) == 1, "expected loaded block content"
        loaded_content = loaded_block[0]
        assert factory.is_bound(
            loaded_content, tdoc
        ), "invalid document binding of loaded block content"
        block_record = loaded_block.block_record
        assert (
            loaded_content.dxf.owner == block_record.dxf.handle
        ), "loaded content has invalid owner handle"
        assert (
            block_record.block.dxf.name == block_record.dxf.name
        ), "block name mismatch of BLOCK_RECORD and BLOCK"
        assert (
            factory.is_bound(block_record.block, tdoc) is True
        ), "BLOCK entity not bound to target doc"
        assert (
            factory.is_bound(block_record.endblk, tdoc) is True
        ), "ENDBLK entity not bound to target doc"

    def test_load_block_layout_does_type_checking(self, sdoc):
        tdoc = ezdxf.new()
        loader = xref.Loader(sdoc, tdoc)

        with pytest.raises(const.DXFTypeError):
            loader.load_block_layout(sdoc.modelspace())

        with pytest.raises(const.DXFTypeError):
            loader.load_block_layout(sdoc.paperspace())

        with pytest.raises(const.DXFTypeError):
            loader.load_block_layout(None)

    def test_load_block_reference(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        assert (
            "TestBlock" in tdoc.blocks
        ), "expected TestBlock layout in target document"
        insert = cast(Insert, tdoc.modelspace()[0])
        assert isinstance(insert, Insert)
        assert factory.is_bound(insert, tdoc), "INSERT entity not bound to target doc"
        assert insert.dxf.name == "TestBlock"
        assert (
            insert.seqend.dxf.owner == insert.dxf.owner
        ), "SEQEND owner should be the INSERT owner"

    def test_load_block_reference_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        insert = cast(Insert, tdoc.modelspace()[0])
        assert len(insert.attribs) == 1, "expected loaded ATTRIB entities"

        attrib = insert.attribs[0]
        assert attrib.dxf.tag == "TestTag"
        assert attrib.dxf.text == "Content"

        assert factory.is_bound(attrib, tdoc), "ATTRIB entity not bound to target doc"
        assert (
            attrib.dxf.owner == insert.dxf.owner
        ), "ATTRIB owner should be the INSERT owner"


class TestAnonymousBlocks:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        anonymous_block = doc.blocks.new_anonymous_block("U")
        doc.modelspace().add_blockref(anonymous_block.dxf.name, insert=(0, 0))
        return doc

    def test_load_anonymous_block(self, sdoc):
        tdoc = ezdxf.new()
        for _ in range(3):  # increase anonymous block name counter
            tdoc.blocks.anonymous_blockname("U")
        xref.load_modelspace(sdoc, tdoc)

        loaded_block_ref = cast(Insert, tdoc.modelspace()[0])
        loaded_block_name = loaded_block_ref.dxf.name
        assert (
            loaded_block_name == "*U4"
        ), "expected next available anonymous block name in tdoc"


def test_load_hard_owned_XRecord_within_appdata_section():
    """Any object which is hard-owned by another entity should automatically be loaded."""
    sdoc = ezdxf.new()
    line = sdoc.modelspace().add_line((0, 0), (1, 0))
    xrec = sdoc.objects.add_xrecord(line.dxf.handle)
    # The LINE entity owns the XRECORD by a hard-owner handle in the app-data
    # section "EZDXF":
    line.set_app_data("EZDXF", [(360, xrec.dxf.handle)])

    tdoc = ezdxf.new()
    xref.load_modelspace(sdoc, tdoc)
    loaded_line = tdoc.modelspace()[0]
    appdata = loaded_line.get_app_data("EZDXF")
    group_code, xrecord_handle = appdata[0]
    assert group_code == 360, "expected the group code of a hard-owner handle"
    loaded_xrecord = tdoc.entitydb.get(xrecord_handle)
    assert loaded_xrecord.dxf.owner == loaded_line.dxf.handle


def test_load_hard_owned_XRecord_by_extension_dict():
    """Any object of the extension dictionary is hard-owned by the entity and should
    automatically be loaded.
    """
    sdoc = ezdxf.new()
    line = sdoc.modelspace().add_line((0, 0), (1, 0))
    xdict = line.new_extension_dict()
    xrec = xdict.add_xrecord("EZDXF")
    xrec.extend([(3, "Content")])

    tdoc = ezdxf.new()
    xref.load_modelspace(sdoc, tdoc)
    loaded_line = tdoc.modelspace()[0]

    loaded_xdict = loaded_line.extension_dict
    assert loaded_xdict is not None
    assert (
        loaded_xdict.dictionary.dxf.owner == loaded_line.dxf.handle
    ), "Extension dictionary should be owned by the loaded entity"
    assert factory.is_bound(loaded_xdict.dictionary, tdoc)

    loaded_xrecord = loaded_xdict["EZDXF"]
    assert factory.is_bound(loaded_xrecord, tdoc)
    assert (
        loaded_xrecord.dxf.owner == loaded_xdict.dictionary.dxf.handle
    ), "XRecord should be owned by the extension dictionary"
    assert loaded_xrecord.tags[0] == (3, "Content")


class TestDimension:
    """Load a simple DIMENSION entity without DIMSTYLE overrides in the XDATA section."""

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new(setup="dimstyles")
        msp = doc.modelspace()
        dim = msp.add_linear_dim(
            base=(3, 2),
            p1=(0, 0),
            p2=(3, 0),
            dimstyle="EZDXF",
        )
        dim.render()
        return doc

    def test_load_dimension_style_exist(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert tdoc.dimstyles.has_entry("EZDXF")

    def test_loaded_geometry_block_exist(self, sdoc):
        source_dim_block_name = sdoc.modelspace()[0].dxf.geometry
        source_block = sdoc.blocks.get(source_dim_block_name)
        assert len(source_block) == 9

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        loaded_dim = tdoc.modelspace()[0]
        geometry = loaded_dim.dxf.geometry
        loaded_block = tdoc.blocks.get(geometry)
        assert len(loaded_block) == 9


# TODO:
# LEADER
# TOLERANCE
# HATCH/MPOLYGON
# IMAGE/IMAGEDEF/IMAGEDEF_REACTOR
# MLINE
# MULTILEADER
# UNDERLAY/UNDERLAYDEFINITION
# VIEWPORT
# Paperspace Layout
# DICTIONARY, test soft-ownership
# XRECORD, register and map pointers and hard-owner handles
# DXFTagStorage, register and map pointers and hard-owner handles
# SORTENTSTABLE
# GEODATA, map block_table_record, linked by extension dictionary of the modelspace
# ACIS entities
# ACAD_PROXY_ENTITY?
# OLE2FRAME?
# SUN?
# IDBUFFER/LAYERFILTER?

if __name__ == "__main__":
    pytest.main([__file__])
