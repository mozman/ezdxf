# Created: 24.03.2010
# Copyright (c) 2010-2019, Manfred Moitzi
# License: MIT License
import pytest

import os
import math
from ezdxf.addons.acadctb import *


class TestPlotStyle:
    def test_init(self):
        style = PlotStyle(0, dict(
            description='memo',
            color_policy=3,
            physical_pen_number=7,
            virtual_pen_number=8,
            screen=99,
            linepattern_size=0.7,
            linetype=17,
            adaptive_linetype=False,
            lineweight=19,
            end_style=1,
            join_style=2,
            fill_style=3
        ))
        assert style.description == 'memo'
        assert style.name == 'Color_1'
        assert style.localized_name == 'Color_1'
        assert style.dithering is True
        assert style.grayscale is True
        assert style.physical_pen_number == 7
        assert style.virtual_pen_number == 8
        assert style.screen == 99
        assert style.linepattern_size == 0.7
        assert style.adaptive_linetype is False
        assert style.lineweight == 19
        assert style.end_style == 1
        assert style.join_style == 2
        assert style.fill_style == 3

    def test_get_set_color(self):
        style = PlotStyle(0)
        style.color = (123, 23, 77)
        assert style.color == (123, 23, 77)

    def test_object_color(self):
        style = PlotStyle(0)
        style.color = (123, 77, 1)
        style.set_object_color()
        assert style.has_object_color()

    def test_dithering(self):
        style = PlotStyle(0)
        style.dithering = True
        assert style.dithering
        style.dithering = False
        assert style.dithering is False

    def test_grayscale(self):
        style = PlotStyle(0)
        style.grayscale = True
        assert style.grayscale
        style.grayscale = False
        assert style.grayscale is False

    def test_dxf_color_index(self):
        style = PlotStyle(0)
        assert style.aci == 1

    def test_set_lineweight(self):
        styles = ColorDependentPlotStyles()
        style = styles[5]
        style.set_lineweight(0.5)
        assert style.lineweight == 13

    def test_write(self):
        expected = ' 0{\n' \
                   '  name="Color_1\n' \
                   '  localized_name="Color_1\n' \
                   '  description="\n' \
                   '  color=-1\n' \
                   '  color_policy=1\n' \
                   '  physical_pen_number=0\n' \
                   '  virtual_pen_number=0\n' \
                   '  screen=100\n' \
                   '  linepattern_size=0.5\n' \
                   '  linetype=31\n' \
                   '  adaptive_linetype=TRUE\n' \
                   '  lineweight=0\n' \
                   '  fill_style=73\n' \
                   '  end_style=4\n' \
                   '  join_style=5\n' \
                   ' }\n'
        style = PlotStyle(0)
        fp = StringIO()
        style.write(fp)
        result = fp.getvalue()
        fp.close()
        assert result == expected


class TestColorDependentPlotStyles:
    @pytest.fixture
    def styles(self):
        return ColorDependentPlotStyles(description='TestCase')

    def test_set_style(self, styles):
        style = styles.new_style(3, dict(description='TestCase'))
        assert style.named_color is False
        assert style.color_type is None
        assert style.description == 'TestCase'

    def test_get_style(self, styles):
        styles.new_style(3, dict(description='TestCase'))
        assert styles[3].description == 'TestCase'

    def test_get_color(self, styles):
        style = styles.new_style(4, dict(description='TestCase'))
        style.color = (123, 17, 99)
        assert style.named_color is False
        assert style.color_type is COLOR_RGB
        assert styles[4].color == (123, 17, 99)

    def test_get_lineweight(self, styles):
        style = styles.new_style(5, dict(description='TestCase'))
        style.set_lineweight(0.70)
        assert math.isclose(styles.get_lineweight(5), 0.70, abs_tol=1e-6)

    def test_get_lineweight_none(self, styles):
        style = styles.new_style(5, dict(description='TestCase'))
        style.set_lineweight(0.0)
        assert styles.get_lineweight(5) is None

    def test_get_lineweight_index(self, styles):
        assert styles.get_lineweight_index(0.50) == 13

    def test_get_table_lineweight(self, styles):
        assert styles.get_table_lineweight(13) == 0.50

    def test_set_table_lineweight(self, styles):
        styles.set_table_lineweight(7, 1.70)
        assert math.isclose(styles.get_table_lineweight(7), 1.70, abs_tol=1e-6)

    def test_set_table_lineweight_index_error(self, styles):
        index_out_of_range = len(styles.lineweights) + 7
        index = styles.set_table_lineweight(index_out_of_range, 7.77)
        assert math.isclose(styles.get_table_lineweight(index), 7.77, abs_tol=1e-6)

    def test_write_header(self):
        expected = 'description="\n' \
                   'aci_table_available=TRUE\n' \
                   'scale_factor=1.0\n' \
                   'apply_factor=FALSE\n' \
                   'custom_lineweight_display_units=0\n'
        styles = ColorDependentPlotStyles()
        fp = StringIO()
        styles._write_header(fp)
        result = fp.getvalue()
        fp.close()
        assert result == expected

    def test_write_aci_table(self):
        expected = 'aci_table{\n' + '\n'.join(
            (' %s="Color_%d' % (index, index + 1)
             for index in range(255))) + '\n}\n'
        styles = ColorDependentPlotStyles()
        fp = StringIO()
        styles._write_aci_table(fp)
        result = fp.getvalue()
        fp.close()
        assert str(result) == str(expected)

    def test_write_lineweights(self):
        expected = 'custom_lineweight_table{\n' \
                   ' 0=0.00\n 1=0.05\n 2=0.09\n 3=0.10\n 4=0.13\n' \
                   ' 5=0.15\n 6=0.18\n 7=0.20\n 8=0.25\n 9=0.30\n' \
                   ' 10=0.35\n 11=0.40\n 12=0.45\n 13=0.50\n 14=0.53\n' \
                   ' 15=0.60\n 16=0.65\n 17=0.70\n 18=0.80\n 19=0.90\n' \
                   ' 20=1.00\n 21=1.06\n 22=1.20\n 23=1.40\n 24=1.58\n' \
                   ' 25=2.00\n 26=2.11\n}\n'
        styles = ColorDependentPlotStyles()
        fp = StringIO()
        styles._write_lineweights(fp)
        result = fp.getvalue()
        fp.close()
        assert str(result) == str(expected)


class TestNamedPlotStyles:
    @pytest.fixture
    def stb(self):
        return NamedPlotStyles(description='TestCase')

    def test_set_style(self, stb):
        style = stb.new_style('ezdxf', dict(description='TestCase'))
        assert style.named_color is True
        assert style.color_type is None
        assert style.description == 'TestCase'

    def test_get_style(self, stb):
        stb.new_style('mozman', dict(description='ezdxf comment'))
        assert stb['mozman'].description == 'ezdxf comment'

    def test_get_color(self, stb):
        style = stb.new_style('mozman2')
        style.color = (123, 17, 99)
        assert style.named_color is True
        # named colors has always color type: COLOR_ACI, why?
        assert style.color_type == COLOR_ACI
        assert stb['mozman2'].color == (123, 17, 99)

    def test_get_lineweight(self, stb):
        style = stb.new_style('mozman5')
        style.set_lineweight(0.70)
        assert math.isclose(stb.get_lineweight('mozman5'), 0.70, abs_tol=1e-6)

    def test_get_lineweight_none(self, stb):
        style = stb.new_style('mozman4')
        style.set_lineweight(0.0)
        assert stb.get_lineweight('mozman4') is None

    def test_get_lineweight_index(self, stb):
        assert stb.get_lineweight_index(0.50) == 13

    def test_get_table_lineweight(self, stb):
        assert stb.get_table_lineweight(13) == 0.50

    def test_set_table_lineweight(self, stb):
        stb.set_table_lineweight(7, 1.70)
        assert math.isclose(stb.get_table_lineweight(7), 1.70, abs_tol=1e-6)

    def test_set_table_lineweight_index_error(self, stb):
        index_out_of_range = len(stb.lineweights) + 7
        index = stb.set_table_lineweight(index_out_of_range, 7.77)
        assert math.isclose(stb.get_table_lineweight(index), 7.77, abs_tol=1e-6)

    def test_write_header(self):
        expected = 'description="\n' \
                   'aci_table_available=FALSE\n' \
                   'scale_factor=1.0\n' \
                   'apply_factor=FALSE\n' \
                   'custom_lineweight_display_units=0\n'
        stb = NamedPlotStyles()
        fp = StringIO()
        stb._write_header(fp)
        result = fp.getvalue()
        fp.close()
        assert result == expected

    def test_write_lineweights(self):
        expected = 'custom_lineweight_table{\n' \
                   ' 0=0.00\n 1=0.05\n 2=0.09\n 3=0.10\n 4=0.13\n' \
                   ' 5=0.15\n 6=0.18\n 7=0.20\n 8=0.25\n 9=0.30\n' \
                   ' 10=0.35\n 11=0.40\n 12=0.45\n 13=0.50\n 14=0.53\n' \
                   ' 15=0.60\n 16=0.65\n 17=0.70\n 18=0.80\n 19=0.90\n' \
                   ' 20=1.00\n 21=1.06\n 22=1.20\n 23=1.40\n 24=1.58\n' \
                   ' 25=2.00\n 26=2.11\n}\n'
        stb = NamedPlotStyles()
        fp = StringIO()
        stb._write_lineweights(fp)
        result = fp.getvalue()
        fp.close()
        assert str(result) == str(expected)


class TestCTBImport:
    @pytest.fixture(scope='class')
    def ctb(self):
        path, name = os.path.split(__file__)
        ctbfile = os.path.join(path, 'ctbtest.ctb')
        return load(ctbfile)

    def test_ctb_attribs(self, ctb):
        styles = ctb
        assert styles.description == 'Comment'
        assert styles.apply_factor is True
        assert styles.scale_factor == 2

    def test_lineweight_table(self, ctb):
        lineweights = ctb.lineweights
        for default_lw, ctb_lw in zip(DEFAULT_LINE_WEIGHTS, lineweights):
            assert math.isclose(default_lw, ctb_lw, abs_tol=1e-6)

    def test_style_1(self, ctb):
        """all attribs are user defined."""
        style = ctb[1]
        assert isinstance(style, PlotStyle)
        assert style.aci == 1
        assert style.color_type == COLOR_RGB
        assert style.color == (235, 135, 20)
        assert style.dithering is True
        assert style.grayscale is True
        assert style.has_object_color() is False
        assert style.physical_pen_number is 11
        assert style.virtual_pen_number == 5
        assert style.screen == 95
        assert style.linetype == 1
        assert style.end_style == END_STYLE_SQUARE
        assert style.join_style == JOIN_STYLE_ROUND
        assert style.fill_style == FILL_STYLE_SOLID

    def test_style_3(self, ctb):
        """all attribs are default or auto"""
        style = ctb[3]
        assert isinstance(style, PlotStyle)
        assert style.aci == 3
        assert style.color_type is None
        assert style.color is None
        assert style.dithering is True
        assert style.grayscale is False
        assert style.has_object_color() is True
        assert style.physical_pen_number == AUTOMATIC
        assert style.virtual_pen_number == AUTOMATIC
        assert style.screen == 100
        assert style.linetype == OBJECT_LINETYPE
        assert style.end_style == END_STYLE_OBJECT
        assert style.join_style == JOIN_STYLE_OBJECT
        assert style.fill_style == FILL_STYLE_OBJECT


class TestCTBExport:
    def test_create_ctb(self, tmpdir):
        filename = str(tmpdir.join('new.ctb'))
        styles = ColorDependentPlotStyles("TestCTB")
        styles.save(filename)
        assert os.path.exists(filename)


class TestSTBImport:
    @pytest.fixture(scope='class')
    def stb(self):
        path, name = os.path.split(__file__)
        stb_file = os.path.join(path, 'stbtest.stb')
        return load(stb_file)

    def test_stb_attribs(self, stb):
        assert stb.description == 'STB file for ezdxf testing'
        assert stb.apply_factor is True
        assert stb.scale_factor == 2

    def test_normal(self, stb):
        """ All attributes of 'Normal' are fixed default values. """
        style = stb['Normal']
        assert isinstance(style, PlotStyle)
        assert style.index == 0
        assert style.color is None
        assert style.dithering is True
        assert style.grayscale is False
        assert style.has_object_color() is True
        assert style.color_type is None
        assert style.physical_pen_number == AUTOMATIC
        assert style.virtual_pen_number == AUTOMATIC
        assert style.screen == 100
        assert style.linetype == OBJECT_LINETYPE
        assert style.lineweight == OBJECT_LINEWEIGHT
        assert style.end_style == END_STYLE_OBJECT
        assert style.join_style == JOIN_STYLE_OBJECT
        assert style.fill_style == FILL_STYLE_OBJECT

    def test_style_1(self, stb):
        """ All attribs are user defined."""
        style = stb['Style_1']
        assert isinstance(style, PlotStyle)
        assert style.name == 'Style_1'
        assert style.localized_name == 'Style 1'
        assert style.color_type == COLOR_ACI   # ???
        assert style.color == (235, 135, 20)
        assert style.named_color is False # why?
        assert style.dithering is True
        assert style.grayscale is True
        assert style.has_object_color() is False
        assert style.physical_pen_number == 11
        assert style.virtual_pen_number == 5
        assert style.screen == 95
        assert style.linetype == 1
        assert style.end_style == END_STYLE_SQUARE
        assert style.join_style == JOIN_STYLE_ROUND
        assert style.fill_style == FILL_STYLE_SOLID

    def test_mozman(self, stb):
        """ All attribs are user defined."""
        style = stb['mozman']
        assert isinstance(style, PlotStyle)
        assert style.name == 'mozman'
        assert style.localized_name == 'mozman'
        assert style.color_type == COLOR_ACI
        assert style.color == (255, 0, 255)
        assert style.named_color is True
        assert style.dithering is True
        assert style.grayscale is False
        assert style.has_object_color() is False
        assert style.physical_pen_number == AUTOMATIC
        assert style.virtual_pen_number == AUTOMATIC
        assert style.screen == 90
        assert style.linetype == 4
        assert style.end_style == END_STYLE_SQUARE
        assert style.join_style == JOIN_STYLE_MITER
        assert style.fill_style == FILL_STYLE_CHECKERBOARD


class TestSTBExport:
    def test_create_ctb(self, tmpdir):
        filename = str(tmpdir.join('new.stb'))
        styles = NamedPlotStyles("TestSTB")
        styles.save(filename)
        assert os.path.exists(filename)


class TestFunctions:
    def test_color_name(self):
        assert color_name(0) == 'Color_1'

    def test_get_bool(self):
        assert get_bool(True)
        assert get_bool('true')
        assert get_bool(False) is False
        assert get_bool('false') is False
        pytest.raises(ValueError, get_bool, 'falsch')
