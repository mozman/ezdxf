#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import xref, colors
from ezdxf.document import Drawing


class TestLoadLayers:
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.layers.add("Layer0", color=colors.RED)
        doc.layers.add("Layer1", color=colors.GREEN)
        doc.layers.add("Layer2", color=colors.BLUE)
        return doc

    @staticmethod
    def load_layers(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_layers(["layer0", "layer1", "layer2"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        """KEEP: Layer0 of the target doc shouldn't be renamed."""
        tdoc = ezdxf.new()
        tdoc.layers.add("Layer0", color=colors.CYAN)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # Layers "0" and "DEFPOINTS" should not be loaded:
        assert len(tdoc.layers) == 3 + 2

        layer0 = tdoc.layers.get("layer0")
        assert layer0.dxf.color == colors.CYAN, "expected Layer0 to be preserved"

    def test_xref_rename_policy(self, sdoc):
        """All layers of the external reference should be renamed.

        Layers "0" and "Defpoints" are always preserved, never renamed.
        """
        tdoc = ezdxf.new()
        tdoc.layers.add("Layer0", color=colors.CYAN)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # Layers "0" and "DEFPOINTS" should not be loaded:
        assert len(tdoc.layers) == 4 + 2

        layer0 = tdoc.layers.get("layer0")
        assert layer0.dxf.color == colors.CYAN, "expected Layer0 to be preserved"

        # check if all loaded layers are renamed:
        xref_layer0 = tdoc.layers.get("xref$0$Layer0")
        assert xref_layer0.dxf.color == colors.RED, "expected loaded Layer0"
        assert tdoc.layers.has_entry("xref$0$Layer1"), "expected loaded Layer1"
        assert tdoc.layers.has_entry("xref$0$Layer2"), "expected loaded Layer2"

    def test_xref_rename_policy_load_2_times(self, sdoc):
        """At the 2nd loading process the layer names conflict with the names of the
        1st loading process.
        """
        tdoc = ezdxf.new()
        tdoc.layers.add("Layer0", color=colors.CYAN)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # check if layers of 2nd loading process exist:
        assert tdoc.layers.has_entry("xref$1$Layer0") is True
        assert tdoc.layers.has_entry("xref$1$Layer1") is True
        assert tdoc.layers.has_entry("xref$1$Layer2") is True

    def test_numbered_rename_policy(self, sdoc):
        """Only layers with name conflicts should be renamed.

        Layers "0" and "Defpoints" are always preserved, never renamed.
        """
        tdoc = ezdxf.new()
        tdoc.layers.add("Layer0", color=colors.CYAN)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        # Layers "0" and "DEFPOINTS" should not be loaded:
        assert len(tdoc.layers) == 4 + 2

        layer0 = tdoc.layers.get("layer0")
        assert layer0.dxf.color == colors.CYAN, "expected Layer0 to be preserved"

        # check if loaded layers with name conflicts are renamed:
        xref_layer0 = tdoc.layers.get("$0$Layer0")
        assert xref_layer0.dxf.color == colors.RED, "expected loaded Layer0"

        # check if loaded layers without name conflicts preserve their names:
        assert tdoc.layers.has_entry("Layer1") is True
        assert tdoc.layers.has_entry("Layer2") is True

    def test_numbered_rename_policy_load_2_times(self, sdoc):
        """At the 2nd loading process the layer names conflict with the names of the
        1st loading process.
        """
        tdoc = ezdxf.new()
        tdoc.layers.add("Layer0", color=colors.CYAN)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)
        self.load_layers(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        assert tdoc.layers.has_entry("Layer0") is True, "expected preserved Layer0"

        # check renaming schema of 1st loading process:
        assert tdoc.layers.has_entry("$0$Layer0") is True
        assert tdoc.layers.has_entry("Layer1") is True
        assert tdoc.layers.has_entry("Layer2") is True

        # check renaming schema of 2nd loading process:
        assert tdoc.layers.has_entry("$1$Layer0") is True
        assert tdoc.layers.has_entry("$0$Layer1") is True
        assert tdoc.layers.has_entry("$0$Layer2") is True


class TestLoadLinetypes:
    """The implementation in the xref module should be the same as for layers, so these
    tests are as minimal as possible.
    """

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.linetypes.add("Ltype0", [0.0], description="xref0")
        doc.linetypes.add("Ltype1", [0.0], description="xref1")
        return doc

    @staticmethod
    def load_linetypes(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_linetypes(["LType0", "LType1"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.linetypes.add("LType0", [0.0], description="preserve")
        self.load_linetypes(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # Linetypes "CONTINUOUS", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.linetypes) == 2 + 3

        ltype0 = tdoc.linetypes.get("LType0")
        assert ltype0.dxf.description == "preserve"
        assert tdoc.linetypes.has_entry("LType1")

    def test_xref_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.linetypes.add("LType0", [0.0], description="preserve")
        self.load_linetypes(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # Linetypes "CONTINUOUS", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.linetypes) == 3 + 3

        ltype0 = tdoc.linetypes.get("LType0")
        assert ltype0.dxf.description == "preserve"
        assert tdoc.linetypes.has_entry("xref$0$LType0") is True
        assert tdoc.linetypes.has_entry("xref$0$LType1") is True

    def test_numbered_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.linetypes.add("LType0", [0.0], description="preserve")
        self.load_linetypes(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        # Linetypes "CONTINUOUS", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.linetypes) == 3 + 3

        ltype0 = tdoc.linetypes.get("LType0")
        assert ltype0.dxf.description == "preserve"
        assert tdoc.linetypes.has_entry("$0$LType0") is True
        assert tdoc.linetypes.has_entry("LType1") is True


class TestLoadTextStyles:
    """The implementation in the xref module should be the same as for layers, so these
    tests are as minimal as possible.
    """

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.styles.add("Style0", font="style0.ttf")
        doc.styles.add("Style1", font="style1.ttf")
        return doc

    @staticmethod
    def load_styles(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_text_styles(["Style0", "Style1"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.styles.add("Style0", font="preserve.ttf")
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.styles) == 1 + 2

        style0 = tdoc.styles.get("Style0")
        assert style0.dxf.font == "preserve.ttf"
        assert tdoc.styles.has_entry("Style1")

    def test_xref_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.styles.add("Style0", font="preserve.ttf")
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.styles) == 3 + 1

        style0 = tdoc.styles.get("Style0")
        assert style0.dxf.font == "preserve.ttf"
        assert tdoc.styles.has_entry("xref$0$Style0") is True
        assert tdoc.styles.has_entry("xref$0$Style1") is True

    def test_numbered_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.styles.add("Style0", font="preserve.ttf")
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.styles) == 3 + 1

        style0 = tdoc.styles.get("Style0")
        assert style0.dxf.font == "preserve.ttf"
        assert tdoc.styles.has_entry("$0$Style0") is True
        assert tdoc.styles.has_entry("Style1") is True


class TestLoadDimStyles:
    """The implementation in the xref module should be the same as for layers, so these
    tests are as minimal as possible.
    """

    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.dimstyles.add("Style0", dxfattribs={"dimpost": "xref"})
        doc.dimstyles.add("Style1", dxfattribs={"dimpost": "xref"})
        return doc

    @staticmethod
    def load_styles(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_dim_styles(["Style0", "Style1"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.dimstyles.add("Style0", dxfattribs={"dimpost": "preserve"})
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.dimstyles) == 1 + 2

        style0 = tdoc.dimstyles.get("Style0")
        assert style0.dxf.dimpost == "preserve"
        assert tdoc.dimstyles.has_entry("Style1")

    def test_xref_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.dimstyles.add("Style0", dxfattribs={"dimpost": "preserve"})
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.dimstyles) == 3 + 1

        style0 = tdoc.dimstyles.get("Style0")
        assert style0.dxf.dimpost == "preserve"
        assert tdoc.dimstyles.has_entry("xref$0$Style0") is True
        assert tdoc.dimstyles.has_entry("xref$0$Style1") is True

    def test_numbered_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.dimstyles.add("Style0", dxfattribs={"dimpost": "preserve"})
        self.load_styles(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        # style "STANDARD" should not be loaded:
        assert len(tdoc.dimstyles) == 3 + 1

        style0 = tdoc.dimstyles.get("Style0")
        assert style0.dxf.dimpost == "preserve"
        assert tdoc.dimstyles.has_entry("$0$Style0") is True
        assert tdoc.dimstyles.has_entry("Style1") is True


class TestLoadMaterials:
    """Materials are stored in object collections which work differently than tables.
    """
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.materials.new("Mat0").dxf.description = "XrefMat0"
        doc.materials.new("Mat1").dxf.description = "XrefMat1"
        return doc

    @staticmethod
    def load_materials(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_materials(["mat0", "mat1"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.materials.new("Mat0").dxf.description = "preserve"
        self.load_materials(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # material "GLOBAL", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.materials) == 3 + 2

        mat0 = tdoc.materials.get("Mat0")
        assert mat0.dxf.description == "preserve"
        assert tdoc.materials.has_entry("Mat1") is True

    def test_xref_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.materials.new("Mat0").dxf.description = "preserve"
        self.load_materials(sdoc, tdoc, xref.ConflictPolicy.XREF_PREFIX)

        # material "GLOBAL", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.materials) == 3 + 3

        mat0 = tdoc.materials.get("Mat0")
        assert mat0.dxf.description == "preserve"
        assert tdoc.materials.has_entry("xref$0$Mat0") is True
        assert tdoc.materials.has_entry("xref$0$Mat1") is True

    def test_numbered_rename_policy(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.materials.new("Mat0").dxf.description = "preserve"
        self.load_materials(sdoc, tdoc, xref.ConflictPolicy.NUM_PREFIX)

        # material "GLOBAL", "BYLAYER" and "BYBLOCK" should not be loaded:
        assert len(tdoc.materials) == 3 + 3

        mat0 = tdoc.materials.get("Mat0")
        assert mat0.dxf.description == "preserve"
        assert tdoc.materials.has_entry("$0$Mat0") is True
        assert tdoc.materials.has_entry("Mat1") is True


class TestLoadMLineStyles:
    """MLineStyles are stored in object collections like Materials."""
    @pytest.fixture(scope="class")
    def sdoc(self) -> Drawing:
        doc = ezdxf.new()
        doc.filename = "xref.dxf"
        doc.mline_styles.new("Style0").dxf.description = "XrefStyle0"
        doc.mline_styles.new("Style1").dxf.description = "XrefStyle1"
        return doc

    @staticmethod
    def load_mline_styles(sdoc, tdoc, policy):
        loader = xref.Loader(sdoc, tdoc, conflict_policy=policy)
        loader.load_mline_styles(["style0", "style1"])
        loader.execute()

    def test_conflict_policy_keep(self, sdoc):
        tdoc = ezdxf.new()
        tdoc.mline_styles.new("Style0").dxf.description = "preserve"
        self.load_mline_styles(sdoc, tdoc, xref.ConflictPolicy.KEEP)

        # style "Standard" should not be loaded:
        assert len(tdoc.mline_styles) == 1 + 2

        style0 = tdoc.mline_styles.get("Style0")
        assert style0.dxf.description == "preserve"
        assert tdoc.mline_styles.has_entry("Style1") is True


if __name__ == "__main__":
    pytest.main([__file__])
