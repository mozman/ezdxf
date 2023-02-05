#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
from collections import Counter
import ezdxf
from ezdxf import xref, colors, const
from ezdxf.math import Vec2
from ezdxf.document import Drawing
from ezdxf.layouts import Paperspace
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.render.arrows import ARROWS
from ezdxf.entities import (
    Polyline,
    Polyface,
    factory,
    Insert,
    Dimension,
    Hatch,
    Image,
    MultiLeader,
    BlockRecord,
    Underlay,
)


def forward_handles(doc, count: int) -> None:
    for _ in range(count):
        doc.entitydb.next_handle()


def document_has_no_errors(doc: Drawing) -> bool:
    auditor = doc.audit()
    return not auditor.has_issues


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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

        assert tdoc.styles.has_entry("ARIAL")

    def test_load_mtext_entity(self, sdoc):
        msp = sdoc.modelspace()
        msp.add_mtext("MyText", dxfattribs={"style": "ARIAL"})
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

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
    assert document_has_no_errors(tdoc) is True

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
        # assert document_has_no_errors(tdoc) is True

        assert tdoc.linetypes.has_entry("LType0")
        loaded_polyline = cast(Polyline, tdoc.modelspace()[0])
        assert isinstance(loaded_polyline, Polyline)
        assert len(loaded_polyline.vertices) == 3
        assert all(
            factory.is_bound(v, tdoc) for v in loaded_polyline.vertices
        ), "all vertices should be bound to tdoc"
        assert all(
            v.dxf.owner == loaded_polyline.dxf.handle for v in loaded_polyline.vertices
        ), "all vertices are owned by the POLYLINE"
        assert (
            loaded_polyline.seqend.dxf.owner == loaded_polyline.dxf.handle
        ), "SEQEND is owned by the POLYLINE"

    def test_load_polyface(self, sdoc):
        polyface = sdoc.modelspace().add_polyface()
        polyface.append_face([(0, 0), (1, 0), (1, 1)])
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True

        assert (
            "TestBlock" in tdoc.blocks
        ), "expected TestBlock layout in target document"
        insert = cast(Insert, tdoc.modelspace()[0])
        assert isinstance(insert, Insert)
        assert factory.is_bound(insert, tdoc), "INSERT entity not bound to target doc"
        assert insert.dxf.name == "TestBlock"
        assert (
            insert.seqend.dxf.owner == insert.dxf.handle
        ), "SEQEND owner should be the INSERT entity"

    def test_load_block_reference_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        insert = cast(Insert, tdoc.modelspace()[0])
        assert len(insert.attribs) == 1, "expected loaded ATTRIB entities"

        attrib = insert.attribs[0]
        assert attrib.dxf.tag == "TestTag"
        assert attrib.dxf.text == "Content"

        assert factory.is_bound(attrib, tdoc), "ATTRIB entity not bound to target doc"
        assert (
            attrib.dxf.owner == insert.dxf.handle
        ), "ATTRIB owner should be the INSERT entity"


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
            tdoc.blocks.anonymous_block_name("U")
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        loaded_block_ref = cast(Insert, tdoc.modelspace()[0])
        loaded_block_name = loaded_block_ref.dxf.name
        assert (
            loaded_block_name == "*U4"
        ), "expected next available anonymous block name in tdoc"


def test_loaded_external_reference():
    sdoc = ezdxf.new()
    sdoc.add_xref_def("my.dxf", "my_xref")
    sdoc.modelspace().add_blockref("my_xref", insert=(0, 0))

    tdoc = ezdxf.new()
    xref.load_modelspace(sdoc, tdoc)

    assert tdoc.block_records.has_entry("my_xref")
    block_layout = tdoc.blocks.get("my_xref")
    assert block_layout.block.is_xref is True
    assert block_layout.block.dxf.xref_path == "my.dxf"

    insert = tdoc.modelspace()[0]
    assert isinstance(insert, Insert)
    assert insert.dxf.name == "my_xref"


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
    assert document_has_no_errors(tdoc) is True

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
    assert document_has_no_errors(tdoc) is True

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
        assert document_has_no_errors(tdoc) is True
        assert tdoc.dimstyles.has_entry("EZDXF")

    def test_loaded_geometry_block_exist(self, sdoc):
        source_dim_block_name = sdoc.modelspace()[0].dxf.geometry
        source_block = sdoc.blocks.get(source_dim_block_name)
        assert len(source_block) == 9

        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        loaded_dim = tdoc.modelspace()[0]
        geometry = loaded_dim.dxf.geometry
        loaded_block = tdoc.blocks.get(geometry)
        assert len(loaded_block) == 9


class TestDimensionDimStyleOverride:
    """Load a DIMENSION with DIMSTYLE overrides in the XDATA section."""

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new(setup="dimstyles")
        msp = doc.modelspace()
        dim = msp.add_linear_dim(
            base=(3, 2),
            p1=(0, 0),
            p2=(3, 0),
            dimstyle="EZDXF",
            override={"dimblk": ARROWS.dot},
        )
        dim.render()
        return doc

    def test_load_dimension_style_exist(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert tdoc.dimstyles.has_entry("EZDXF")

    def test_dot_blocks_in_source_doc(self, sdoc):
        source_dim_block_name = sdoc.modelspace()[0].dxf.geometry
        source_block = sdoc.blocks.get(source_dim_block_name)
        counter = Counter(
            block_ref.dxf.name for block_ref in source_block.query("INSERT")
        )
        assert counter["_DOT"] == 2

    def test_loaded_geometry_block_has_two_block_refs_of_dot(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        assert tdoc.block_records.has_entry("_DOT")
        loaded_dim = tdoc.modelspace()[0]
        geometry = loaded_dim.dxf.geometry
        loaded_block = tdoc.blocks.get(geometry)
        counter = Counter(
            block_ref.dxf.name for block_ref in loaded_block.query("INSERT")
        )
        assert counter["_DOT"] == 2

    def test_loaded_xdata_override_has_handle_to_existing_block(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        loaded_dim = cast(Dimension, tdoc.modelspace()[0])
        override_tags = loaded_dim.get_xdata_list("ACAD", "DSTYLE")

        handles = [value for code, value in override_tags if code == 1005]
        assert len(handles) == 1

        block_record = tdoc.entitydb.get(handles[0])
        assert block_record.dxf.name == "_DOT"


class TestLeader:
    """Load a LEADER with DIMSTYLE overrides in the XDATA section.

    Note: loading a LEADER entity does not automatically trigger the import of the
    linked TEXT, TOLERANCE or BLOCK entity, only handles are mapped correctly.

    """

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new(setup="dimstyles")
        msp = doc.modelspace()
        text = msp.add_text("LEADER").set_placement((3, 1))
        msp.add_leader(
            vertices=[(0, 0), (1, 1), (2, 1)],
            dimstyle="EZDXF",
            override={"dimldrblk": ARROWS.dot},
            dxfattribs={"annotation_type": 0, "annotation_handle": text.dxf.handle},
        )
        return doc

    def test_loaded_leader_is_linked_to_loaded_text(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        text, leader = tdoc.modelspace()
        assert leader.dxf.annotation_handle == text.dxf.handle

    def test_loaded_xdata_override_has_handle_to_existing_block(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True

        text, leader = tdoc.modelspace()
        override_tags = leader.get_xdata_list("ACAD", "DSTYLE")

        handles = [value for code, value in override_tags if code == 1005]
        assert len(handles) == 1

        block_record = tdoc.entitydb.get(handles[0])
        assert block_record.dxf.name == "_DOT"


def test_tolerance_entity_register_dimstyle():
    from ezdxf.entities import Tolerance

    sdoc = ezdxf.new(setup="dimstyles")
    msp = sdoc.modelspace()

    # no factory method exist:
    tolerance = Tolerance.new(dxfattribs={"dimstyle": "EZDXF"}, doc=sdoc)
    msp.add_entity(tolerance)

    tdoc = ezdxf.new()
    xref.load_modelspace(sdoc, tdoc)
    assert document_has_no_errors(tdoc) is True
    assert tdoc.dimstyles.has_entry("EZDXF")


def test_associative_hatch_has_updated_source_boundary_handles():
    sdoc = ezdxf.new()
    msp = sdoc.modelspace()
    line0 = msp.add_line((0, 0), (2, 1))
    line1 = msp.add_line((2, 1), (1, 2))
    line2 = msp.add_line((1, 2), (0, 0))
    hatch = msp.add_hatch()
    path = hatch.paths.add_polyline_path([(0, 0), (2, 1), (1, 2)])
    path.source_boundary_objects = [e.dxf.handle for e in (line0, line1, line2)]

    tdoc = ezdxf.new()
    xref.load_modelspace(sdoc, tdoc)
    assert document_has_no_errors(tdoc) is True

    loaded_hatch = cast(Hatch, tdoc.modelspace().query("HATCH").first)
    loaded_handles = loaded_hatch.paths[0].source_boundary_objects

    assert len(loaded_handles) == 3
    assert all(h in tdoc.entitydb for h in loaded_handles)


class TestLoadImage:
    """Load a IMAGE, IMAGEDEF and IMAGEDEF_REACTOR"""

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        msp = doc.modelspace()
        my_image_def = doc.add_image_def(
            filename="example.jpg", size_in_pixel=(640, 360)
        )
        msp.add_image(  # first image
            image_def=my_image_def, insert=(4, 5), size_in_units=(3.2, 1.8), rotation=30
        )
        msp.add_image(  # second image
            image_def=my_image_def, insert=(10, 5), size_in_units=(6.4, 3.6), rotation=0
        )
        return doc

    def test_loaded_infrastructure(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert "ACAD_IMAGE_VARS" in tdoc.rootdict, "expected required image vars"
        assert (
            len(tdoc.objects.query("IMAGEDEF_REACTOR")) == 2
        ), "expected two IMAGEDEF_REACTOR objects"
        assert len(tdoc.objects.query("IMAGEDEF")) == 1, "expected one IMAGEDEF object"

    def test_loaded_images_share_image_definition(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        image0, image1 = tdoc.modelspace()
        assert isinstance(image0, Image)
        assert isinstance(image1, Image)

        image0_def = image0.image_def
        assert image0_def.dxf.filename == "example.jpg"
        assert factory.is_bound(image0_def, tdoc)
        assert image0_def is image1.image_def

    def test_loaded_image_def_reactors(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        image0, image1 = tdoc.modelspace()
        assert isinstance(image0, Image)
        assert isinstance(image1, Image)

        # IMAGEDEF_REACTOR for image0
        assert factory.is_bound(image0.image_def_reactor, tdoc)
        assert image0.image_def_reactor.dxf.image_handle == image0.dxf.handle

        # IMAGEDEF_REACTOR for image1
        assert factory.is_bound(image1.image_def_reactor, tdoc)
        assert image1.image_def_reactor.dxf.image_handle == image1.dxf.handle

        # IMAGEDEF_REACTOR in IMAGEDEF reactor handles
        assert image0.image_def_reactor.dxf.handle in image0.image_def.get_reactors()
        assert image1.image_def_reactor.dxf.handle in image1.image_def.get_reactors()


class TestLoadWipeout:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        msp = doc.modelspace()
        msp.add_wipeout(vertices=[(0, 0), (2, 1), (1, 1)])
        return doc

    def test_loaded_infrastructure(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert "ACAD_WIPEOUT_VARS" in tdoc.rootdict, "expected required wipeout vars"

    def test_loaded_wipeout_has_same_boundary_path(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        source_wipeout = sdoc.modelspace()[0]
        loaded_wipeout = tdoc.modelspace()[0]

        assert all(
            v0.isclose(v1)
            for v0, v1 in zip(
                source_wipeout.boundary_path, loaded_wipeout.boundary_path
            )
        )
        # these handles are always "0"
        assert loaded_wipeout.dxf.image_def_reactor_handle == "0"
        assert loaded_wipeout.dxf.image_def_handle == "0"


class TestLoadMLine:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        style = doc.mline_styles.new("above")
        style.elements.append(0.5, 1)
        style.elements.append(0.25, 3)

        msp = doc.modelspace()
        msp.add_mline(
            [(0, 0), (10, 0), (15, 5), (15, 10)],
            dxfattribs={
                "style_name": style.dxf.name,
                "justification": const.MLINE_BOTTOM,
            },
        )
        return doc

    def test_loaded_infrastructure(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert "above" in tdoc.mline_styles

    def test_loaded_mline_has_correct_style_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        loaded_mline = tdoc.modelspace()[0]
        assert loaded_mline.style.dxf.name == "above"
        assert (
            loaded_mline.dxf.style_handle == tdoc.mline_styles.get("above").dxf.handle
        )

    def test_loaded_mline_has_same_vertices(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        source_mline = sdoc.modelspace()[0]
        loaded_mline = tdoc.modelspace()[0]
        assert all(
            v0.isclose(v1)
            for v0, v1 in zip(
                source_mline.get_locations(), loaded_mline.get_locations()
            )
        )


MTEXT_STYLE = "EZDXF_MTEXT"


class TestMultiLeaderMText:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        msp = doc.modelspace()

        doc.styles.add("OpenSans", font="OpenSans-Regular.ttf")
        mleader_style = doc.mleader_styles.duplicate_entry("Standard", MTEXT_STYLE)
        mleader_style.set_mtext_style("OpenSans")
        mleader_style.set_arrow_head(ARROWS.dot)
        mleader_style.set_leader_properties(linetype="CONTINUOUS")
        ml_builder = msp.add_multileader_mtext(MTEXT_STYLE)
        ml_builder.quick_leader(
            "MTEXT CONTENT", target=Vec2(40, 15), segment1=Vec2.from_deg_angle(45, 14)
        )
        return doc

    def test_loaded_infrastructure(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert tdoc.styles.has_entry("OpenSans") is True
        assert MTEXT_STYLE in tdoc.mleader_styles

    def test_loaded_mleader_mtext_style(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        loaded_mleader_style = tdoc.mleader_styles.get(MTEXT_STYLE)
        assert loaded_mleader_style.dxf.name == MTEXT_STYLE

        text_style = tdoc.styles.get("OpenSans")
        assert loaded_mleader_style.dxf.text_style_handle == text_style.dxf.handle

        ltype = tdoc.linetypes.get("CONTINUOUS")
        assert loaded_mleader_style.dxf.leader_linetype_handle == ltype.dxf.handle

        arrow_head_handle = loaded_mleader_style.dxf.arrow_head_handle
        arrow_head_block_record = tdoc.entitydb.get(arrow_head_handle)
        assert isinstance(arrow_head_block_record, BlockRecord)
        assert arrow_head_block_record.dxf.name == ARROWS.block_name(ARROWS.dot)

    def test_loader_multileader_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        db = tdoc.entitydb
        loaded_mleader: MultiLeader = tdoc.modelspace()[0]

        mleader_style = db.get(loaded_mleader.dxf.style_handle)
        assert mleader_style.dxf.name == MTEXT_STYLE, "invalid mleader_style_handle"

        ltype = db.get(loaded_mleader.dxf.leader_linetype_handle)
        assert ltype.dxf.name.upper() == "CONTINUOUS", "invalid linetype handle"

        text_style = db.get(loaded_mleader.dxf.text_style_handle)
        assert text_style.dxf.name == "OpenSans", "invalid text style handle"

        arrow_head = db.get(loaded_mleader.dxf.arrow_head_handle)
        assert arrow_head.dxf.name == ARROWS.block_name(
            ARROWS.dot
        ), "invalid arrowhead handle"

        assert (
            loaded_mleader.dxf.block_record_handle == "0"
        ), "expected null-ptr as block record handle"

        mtext_data = loaded_mleader.context.mtext
        assert (
            mtext_data.style_handle == text_style.dxf.handle
        ), "MTEXT data has invalid text style handle"

        assert mtext_data.default_content == "MTEXT CONTENT"


BLOCK_STYLE = "EZDXF_BLOCK"


class TestMultiLeaderBlock:
    @staticmethod
    def create_block(doc, name: str, size: float = 8, margin: float = 0.25):
        from ezdxf.render import forms
        from ezdxf.enums import TextEntityAlignment

        block = doc.blocks.new(name, base_point=(0, 0))
        block.add_lwpolyline(forms.square(size), close=True)
        attdef_attribs = {"height": 1.0, "style": "OpenSans"}
        bottom_left_attdef = block.add_attdef(
            "ONE", text="ONE", dxfattribs=attdef_attribs
        )
        bottom_left_attdef.set_placement(
            (margin, margin), align=TextEntityAlignment.BOTTOM_LEFT
        )
        top_right_attdef = block.add_attdef(
            "TWO", text="TWO", dxfattribs=attdef_attribs
        )
        top_right_attdef.set_placement(
            (size - margin, size - margin), align=TextEntityAlignment.TOP_RIGHT
        )
        return block

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        from ezdxf.render import mleader

        doc = ezdxf.new()
        msp = doc.modelspace()

        doc.styles.add("OpenSans", font="OpenSans-Regular.ttf")
        block = self.create_block(doc, "SQUARE")

        mleader_style = doc.mleader_styles.duplicate_entry("Standard", BLOCK_STYLE)
        mleader_style.dxf.block_record_handle = block.block_record_handle

        ml_builder = msp.add_multileader_block(style=BLOCK_STYLE)
        ml_builder.set_content(name=block.name)
        ml_builder.set_attribute("ONE", "Data1")
        ml_builder.set_attribute("TWO", "Data2")
        ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(20, 10)])
        ml_builder.build(insert=Vec2(5, 2))
        return doc

    def test_loaded_mleader_block_style(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        loaded_mleader_style = tdoc.mleader_styles.get(BLOCK_STYLE)
        assert loaded_mleader_style.dxf.name == BLOCK_STYLE

        block_record_handle = loaded_mleader_style.dxf.block_record_handle
        loaded_block = tdoc.blocks.get("SQUARE")
        assert loaded_block.block_record_handle == block_record_handle

    def test_loaded_mleader_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        db = tdoc.entitydb
        loaded_mleader: MultiLeader = tdoc.modelspace()[0]
        block_record_handle = loaded_mleader.dxf.block_record_handle

        loaded_block_record = db.get(block_record_handle)
        assert isinstance(loaded_block_record, BlockRecord)
        assert loaded_block_record.dxf.name == "SQUARE"

        block_data = loaded_mleader.context.block
        assert block_data.block_record_handle == block_record_handle

    def test_loaded_block_attributes(self, sdoc):
        """Block attributes are virtual ATTRIB entities attached to the MLEADER BLOCK,
        created by the DXF renderer from ATTDEF entities in the BLOCK definition.

        """
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        loaded_mleader: MultiLeader = tdoc.modelspace()[0]
        block = tdoc.blocks.get("SQUARE")

        attdef0, attdef1 = block.query("ATTDEF")
        block_attrib0, block_attrib1 = loaded_mleader.block_attribs

        assert attdef0.dxf.handle == block_attrib0.handle
        assert attdef1.dxf.handle == block_attrib1.handle

        assert block_attrib0.text == "Data1"
        assert block_attrib1.text == "Data2"


class TestUnderlay:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        pdf_underlay_def = doc.add_underlay_def(
            filename="underlay.pdf", name="1"
        )  # name = page to display
        msp = doc.modelspace()
        msp.add_underlay(pdf_underlay_def, insert=(0, 0, 0), scale=1.0)
        msp.add_underlay(pdf_underlay_def, insert=(10, 0, 0), scale=2.0)
        return doc

    def test_loaded_infrastructure(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        assert document_has_no_errors(tdoc) is True
        assert "ACAD_PDFDEFINITIONS" in tdoc.rootdict
        acad_dict = tdoc.rootdict.get("ACAD_PDFDEFINITIONS")
        assert len(acad_dict) == 1, "expected one loaded pdf definition"

    def test_loaded_attributes(self, sdoc):
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)
        pdf_underlay0, pdf_underlay1 = tdoc.modelspace()
        assert isinstance(pdf_underlay0, Underlay)
        assert isinstance(pdf_underlay1, Underlay)

        pdf_definition = pdf_underlay0.get_underlay_def()
        assert pdf_definition.dxf.handle == pdf_underlay0.dxf.underlay_def_handle
        assert pdf_definition.dxf.handle == pdf_underlay1.dxf.underlay_def_handle
        assert pdf_underlay0.get_underlay_def() is pdf_underlay1.get_underlay_def()


class TestLoadPaperspaceLayout:
    @pytest.fixture(scope="class")
    def psp(self) -> Paperspace:
        doc = ezdxf.new()
        psp = doc.new_layout("MyLayout")
        psp.add_line((0, 0), (1, 0))
        return psp

    def test_loaded_infrastructure(self, psp):
        tdoc = ezdxf.new()
        xref.load_paperspace(psp, tdoc)
        assert document_has_no_errors(tdoc) is True

        loaded_psp = tdoc.paperspace("MyLayout")
        assert isinstance(loaded_psp, Paperspace)

    def test_loaded_paperspace_without_name_conflict(self, psp):
        tdoc = ezdxf.new()
        xref.load_paperspace(psp, tdoc)
        assert document_has_no_errors(tdoc) is True

        loaded_psp = tdoc.paperspace("MyLayout")
        assert isinstance(loaded_psp, Paperspace)

        assert loaded_psp.name == "MyLayout"
        assert loaded_psp.name in loaded_psp.doc.layouts

        block_record = loaded_psp.block_record
        assert block_record.dxf.name == "*Paper_Space0"
        assert loaded_psp.doc.block_records.has_entry("*Paper_Space0")

        # does the required block layout structure exist:
        block_layout = loaded_psp.doc.blocks.get("*Paper_Space0")
        assert block_layout.is_any_paperspace is True

        # check valid link structures
        dxf_layout = loaded_psp.dxf_layout
        assert block_record.dxf.layout == dxf_layout.dxf.handle
        assert dxf_layout.dxf.block_record_handle == block_record.dxf.handle

    def test_loaded_paperspace_content(self, psp):
        tdoc = ezdxf.new()
        xref.load_paperspace(psp, tdoc)
        loaded_psp = tdoc.paperspace("MyLayout")
        assert len(loaded_psp) == 1
        line = loaded_psp[0]
        assert line.dxftype() == "LINE"
        assert factory.is_bound(line, tdoc)

    def test_paperspace_name_conflict(self, psp):
        tdoc = ezdxf.new()
        tdoc.layouts.new("MyLayout")  # *Paper_Space0

        xref.load_paperspace(psp, tdoc)
        loaded_psp = tdoc.paperspace("MyLayout (2)")
        assert isinstance(loaded_psp, Paperspace)

        assert loaded_psp.name == "MyLayout (2)"
        assert loaded_psp.name in loaded_psp.doc.layouts

        block_record = loaded_psp.block_record
        assert block_record.dxf.name == "*Paper_Space1"
        assert loaded_psp.doc.block_records.has_entry("*Paper_Space1")


# TODO:
# VIEWPORT
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
