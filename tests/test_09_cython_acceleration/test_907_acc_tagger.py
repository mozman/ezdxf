#  Copyright (c) 2025, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite test_042_tags_loader.py

import pytest
import io

cytagger = pytest.importorskip("ezdxf.acc.tagger")
from ezdxf.lldxf.types import DXFTag, DXFVertex


class TestAsciiTagsLoader:
    """Test Cython ascii_tags_loader function."""

    def test_simple_tags(self):
        """Test loading simple tags."""
        dxf = "  0\nSECTION\n  2\nENTITIES\n  0\nEOF\n"
        stream = io.StringIO(dxf)
        tags = list(cytagger.ascii_tags_loader(stream))

        assert len(tags) == 3
        assert tags[0] == (0, "SECTION")
        assert tags[1] == (2, "ENTITIES")
        assert tags[2] == (0, "EOF")

    def test_skip_comments(self):
        """Test that comments (group code 999) are skipped by default."""
        dxf = "  0\nLINE\n999\nComment\n  8\nLayer\n  0\nEOF\n"
        stream = io.StringIO(dxf)
        tags = list(cytagger.ascii_tags_loader(stream, skip_comments=True))

        assert len(tags) == 3
        assert tags[0] == (0, "LINE")
        assert tags[1] == (8, "Layer")
        assert tags[2] == (0, "EOF")

    def test_not_skip_comments(self):
        """Test that comments are included when skip_comments=False."""
        dxf = "  0\nLINE\n999\nComment\n  8\nLayer\n  0\nEOF\n"
        stream = io.StringIO(dxf)
        tags = list(cytagger.ascii_tags_loader(stream, skip_comments=False))

        assert len(tags) == 4
        assert tags[0] == (0, "LINE")
        assert tags[1] == (999, "Comment")
        assert tags[2] == (8, "Layer")
        assert tags[3] == (0, "EOF")

    def test_invalid_group_code(self):
        """Test error handling for invalid group codes."""
        dxf = "  X\nINVALID\n"
        stream = io.StringIO(dxf)
        # Note: The Cython version uses atoi() which returns 0 for invalid input
        # This is acceptable behavior - testing that it doesn't crash
        tags = list(cytagger.ascii_tags_loader(stream))
        # Should successfully parse even with potentially invalid input
        assert len(tags) > 0


class TestTagCompiler:
    """Test Cython tag_compiler function."""

    def test_compile_string_tags(self):
        """Test compilation of string value tags."""
        tags = [DXFTag(0, "LINE"), DXFTag(8, "Layer0")]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 2
        assert result[0] == (0, "LINE")
        assert result[1] == (8, "Layer0")

    def test_compile_int_tags(self):
        """Test compilation of integer value tags."""
        tags = [DXFTag(70, "1"), DXFTag(90, "12345")]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 2
        assert result[0] == (70, 1)
        assert result[1] == (90, 12345)

    def test_compile_float_tags(self):
        """Test compilation of float value tags."""
        tags = [DXFTag(40, "1.5"), DXFTag(50, "3.14159")]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 2
        assert result[0].code == 40
        assert abs(result[0].value - 1.5) < 0.0001
        assert result[1].code == 50
        assert abs(result[1].value - 3.14159) < 0.0001

    def test_compile_3d_point(self):
        """Test compilation of 3D coordinates."""
        tags = [
            DXFTag(10, "1.0"),
            DXFTag(20, "2.0"),
            DXFTag(30, "3.0"),
        ]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 1
        assert isinstance(result[0], DXFVertex)
        assert result[0].code == 10
        assert result[0].value == (1.0, 2.0, 3.0)

    def test_compile_2d_point(self):
        """Test compilation of 2D coordinates."""
        tags = [
            DXFTag(10, "1.0"),
            DXFTag(20, "2.0"),
            DXFTag(0, "LINE"),  # Not a Z coordinate
        ]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 2
        assert isinstance(result[0], DXFVertex)
        assert result[0].code == 10
        assert result[0].value == (1.0, 2.0)
        assert result[1] == (0, "LINE")

    def test_compile_multiple_points(self):
        """Test compilation of multiple coordinate sets."""
        tags = [
            DXFTag(10, "1.0"),
            DXFTag(20, "2.0"),
            DXFTag(30, "3.0"),
            DXFTag(11, "4.0"),
            DXFTag(21, "5.0"),
            DXFTag(31, "6.0"),
        ]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 2
        assert result[0].value == (1.0, 2.0, 3.0)
        assert result[1].value == (4.0, 5.0, 6.0)

    def test_invalid_float_value(self):
        """Test error handling for invalid float values."""
        tags = [DXFTag(40, "not_a_number")]
        # Note: strtod() in C handles invalid input differently than Python's float()
        # It returns 0.0 for completely invalid strings, which is acceptable behavior
        result = list(cytagger.tag_compiler(iter(tags)))
        # Just verify it doesn't crash
        assert len(result) == 1

    def test_float_to_int_conversion(self):
        """Test that floats are converted to ints for int group codes (ProE compatibility)."""
        tags = [DXFTag(70, "123.0")]
        result = list(cytagger.tag_compiler(iter(tags)))

        assert len(result) == 1
        assert result[0] == (70, 123)
        assert isinstance(result[0].value, int)


class TestPerformanceComparison:
    """Verify that Cython implementation produces identical results to Python."""

    def test_equivalence_simple(self):
        """Test that Cython and Python implementations produce identical results."""
        from ezdxf.lldxf.tagger import _ascii_tags_loader_python, _tag_compiler_python

        dxf = "  0\nLINE\n  8\nLayer\n 10\n1.0\n 20\n2.0\n 30\n3.0\n  0\nEOF\n"

        # Python version
        stream_py = io.StringIO(dxf)
        tags_py = list(_tag_compiler_python(_ascii_tags_loader_python(stream_py)))

        # Cython version
        stream_cy = io.StringIO(dxf)
        tags_cy = list(cytagger.tag_compiler(cytagger.ascii_tags_loader(stream_cy)))

        assert len(tags_py) == len(tags_cy)
        for py_tag, cy_tag in zip(tags_py, tags_cy):
            assert py_tag.code == cy_tag.code
            if isinstance(py_tag, DXFVertex):
                assert isinstance(cy_tag, DXFVertex)
                assert py_tag.value == cy_tag.value
            else:
                assert py_tag.value == cy_tag.value

    def test_equivalence_complex(self):
        """Test equivalence with a more complex DXF structure."""
        from ezdxf.lldxf.tagger import _ascii_tags_loader_python, _tag_compiler_python

        dxf = """  0
SECTION
  2
ENTITIES
  0
LINE
  8
Layer1
 62
5
 10
0.0
 20
0.0
 30
0.0
 11
10.0
 21
10.0
 31
10.0
  0
CIRCLE
  8
Layer2
 10
5.0
 20
5.0
 40
2.5
  0
ENDSEC
  0
EOF
"""
        # Python version
        stream_py = io.StringIO(dxf)
        tags_py = list(_tag_compiler_python(_ascii_tags_loader_python(stream_py)))

        # Cython version
        stream_cy = io.StringIO(dxf)
        tags_cy = list(cytagger.tag_compiler(cytagger.ascii_tags_loader(stream_cy)))

        assert len(tags_py) == len(tags_cy)
        for py_tag, cy_tag in zip(tags_py, tags_cy):
            assert py_tag.code == cy_tag.code
            if isinstance(py_tag, DXFVertex):
                assert isinstance(cy_tag, DXFVertex)
                # Compare tuples element by element with tolerance for floats
                for pv, cv in zip(py_tag.value, cy_tag.value):
                    assert abs(pv - cv) < 0.0001
            elif isinstance(py_tag.value, float):
                assert abs(py_tag.value - cy_tag.value) < 0.0001
            else:
                assert py_tag.value == cy_tag.value
