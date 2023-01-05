#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf import xref, colors
from ezdxf.tools.standards import setup_dimstyle
from ezdxf.render.arrows import ARROWS
from ezdxf.entities import Polyline, Polyface


def forward_handles(doc, count: int) -> None:
    for _ in range(count):
        doc.entitydb.next_handle()


class TestLoadResourcesWithoutNamingConflicts:
    @pytest.fixture(scope="class")
    def sdoc(self):
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
    def sdoc(self):
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
    def sdoc(self):
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

    copy = tdoc.modelspace()[0]
    assert copy.has_columns is True
    columns = copy.columns.linked_columns
    assert len(columns) == 2
    assert columns[0].doc is tdoc
    assert columns[0].dxf.handle in tdoc.entitydb
    assert columns[1].doc is tdoc
    assert columns[1].dxf.handle in tdoc.entitydb


class TestLoadLinkedEntities:
    @pytest.fixture
    def sdoc(self):
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
        copy = cast(Polyline, tdoc.modelspace()[0])
        assert isinstance(copy, Polyline)
        assert len(copy.vertices) == 3
        assert all(v.doc is tdoc for v in copy.vertices)

    def test_load_polyface(self, sdoc):
        polyface = sdoc.modelspace().add_polyface()
        polyface.append_face([(0, 0), (1, 0), (1, 1)])
        tdoc = ezdxf.new()
        xref.load_modelspace(sdoc, tdoc)

        copy = cast(Polyface, tdoc.modelspace()[0])
        assert isinstance(copy, Polyface)
        faces = list(copy.faces())
        assert len(faces[0]) == 3 + 1  # vertices + face-record
        assert all(v.doc is tdoc for v in copy.vertices)


# TODO:
# Name conflict handling
# LEADER
# TOLERANCE
# INSERT/BLOCKS
# DIMENSION
# HATCH/MPOLYGON
# IMAGE/IMAGEDEF/IMAGEDEF_REACTOR
# MLINE
# MULTILEADER
# UNDERLAY/UNDERLAYDEFINITION
# VIEWPORT
# Paperspace Layout
# SORTENTSTABLE
# GEODATA?, linked by extension dictionary of the modelspace
# ACIS entities
# ACAD_PROXY_ENTITY?
# OLE2FRAME?
# SUN?
# IDBUFFER/LAYERFILTER?

if __name__ == "__main__":
    pytest.main([__file__])
