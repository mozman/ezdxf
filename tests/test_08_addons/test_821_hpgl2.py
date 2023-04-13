#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons.hpgl2 import api
from ezdxf.addons.hpgl2.properties import RGB, FillType
from ezdxf.addons.hpgl2.backend import Backend
from ezdxf.addons.hpgl2.deps import Vec2
from ezdxf.addons.hpgl2.page import Page

def test_parse_hpgl_commands():
    s = b"%-1BBP;IN;DF;LA1,4,2,6;FT1;PS38812,33987;IP0,0,38812,33987;PU;PA0,0;PUSP0PG;"
    commands = api.hpgl2_commands(s)
    assert len(commands) == 12

def test_skip_all_pcl5_commands():
    s = b"xxxxxyyyy%-1BBPINescape***%1BDF"
    commands = api.hpgl2_commands(s)
    assert len(commands) == 3
    assert commands[0].name == "BP"
    assert commands[1].name == "IN"
    assert commands[2].name == "DF"

def debug():
    from pathlib import Path
    s = Path(r"C:\Users\mozman\Desktop\Outbox\W2 - 6002.plt").read_bytes()
    commands = api.hpgl2_commands(s)
    assert len(commands) == 0

class MyBackend(Backend):
    def __init__(self):
        self.result = []

    def draw_polyline(self, properties, points) -> None:
        self.result.append(["Polyline", points])

    def draw_filled_polygon_buffer(self, properties, paths) -> None:
        self.result.append(["FilledPolygon", paths])

    def draw_outline_polygon_buffer(self, properties, paths) -> None:
        self.result.append(["OutlinePolygon", paths])


def plot(s: bytes):
    commands = api.hpgl2_commands(s)
    backend = MyBackend()
    api.Plotter(backend)
    plotter = api.Plotter(backend)
    interpreter = api.Interpreter(plotter)
    interpreter.run(commands)
    return interpreter


def get_result(plotter):
    return plotter.backend.result


class TestRenderEngine:
    @pytest.mark.parametrize("cmd", [b"PD;PA2000,8000;", b"PU;PA2000,8000;"])
    def test_pen_absolute(self, cmd):
        ip = plot(cmd)
        assert ip.plotter.user_location == Vec2(2000, 8000)

    def test_select_pen(self):
        ip = plot(b"SP7;")
        assert ip.plotter.properties.pen_index == 7

        ip = plot(b"PC3,20,30,40;PW0.18,3;SP3;")
        properties = ip.plotter.properties
        assert properties.pen_index == 3
        assert properties.pen_width == 0.18
        assert properties.pen_color == RGB(20, 30, 40)

    def test_set_pen_width(self):
        ip = plot(b"PW0.18,2;")
        properties = ip.plotter.properties

        assert properties.pen_width == properties.DEFAULT_PEN.width
        pen = properties.get_pen(2)
        assert pen.width == 0.18

    def test_set_current_pen_width(self):
        ip = plot(b"PW0.18;")
        assert ip.plotter.properties.pen_width == 0.18

    def test_set_pen_color(self):
        ip = plot(b"PC2,20,30,40;")
        pen = ip.plotter.properties.get_pen(2)
        assert pen.color == RGB(20, 30, 40)
        assert (
            ip.plotter.properties.pen_color == ip.plotter.properties.DEFAULT_PEN.color
        )

    def test_set_fill_type_hatching(self):
        ip = plot(b"FT3,80,45;")
        props = ip.plotter.properties
        assert props.fill_type == FillType.HATCHING
        assert props.fill_hatch_line_spacing == 80
        assert props.fill_hatch_line_angle == 45

    def test_set_fill_type_shading(self):
        ip = plot(b"FT10,37;")
        props = ip.plotter.properties
        assert props.fill_type == FillType.SHADING
        assert props.fill_shading_density == 37

    def test_pen_relative(self):
        ip = plot(b"PA1000,1000;PR500,-500;")
        assert ip.plotter.user_location == Vec2(1500, 500)

    def test_polyline(self):
        ip = plot(b"PD2000,8000,4000,2000,5000,5000;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        points = command[1]
        assert len(points) == 4
        assert points[0] == Vec2(0, 0)
        assert points[3] == Vec2(5000, 5000)
        assert ip.plotter.user_location == Vec2(5000, 5000)

    def test_cubic_bezier_curve_pen_down(self):
        ip = plot(b"PD;BZ2000,8000,4000,2000,5000,5000;")
        command = get_result(ip.plotter)[0]
        points = command[1]
        assert command[0] == "Polyline"
        assert points[0] == Vec2(0, 0)
        assert points[-1] == Vec2(5000, 5000)
        assert ip.plotter.user_location == Vec2(5000, 5000)

    def test_cubic_bezier_curve_pen_up(self):
        ip = plot(b"PU;BZ2000,8000,4000,2000,5000,5000;")
        assert len(get_result(ip.plotter)) == 0
        assert ip.plotter.user_location == Vec2(5000, 5000)

    def test_circle(self):
        ip = plot(b"PU;PA2000,8000;PD;CI500;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        assert len(command[1]) == 73  # default chord_angle is 5 deg
        assert ip.plotter.user_location == Vec2(2000, 8000)

    def test_abs_arc(self):
        ip = plot(b"PU100,100;PD;AA200,100,-180;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        assert len(command[1]) == 37  # default chord_angle is 5 deg
        assert ip.plotter.user_location.isclose((300, 100))

    def test_rel_arc(self):
        ip = plot(b"PU100,100;PD;AR100,0,-180;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        assert len(command[1]) == 37  # default chord_angle is 5 deg
        assert ip.plotter.user_location.isclose((300, 100))

    def test_abs_arc_three_points_clockwise(self):
        ip = plot(b"PU100,100;PD;AT200,200,300,100;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        points = command[1]
        assert len(points) == 37  # default chord_angle is 5 deg
        assert points[18].isclose((200, 200))
        assert ip.plotter.user_location.isclose((300, 100))

    def test_abs_arc_three_points_counter_clockwise(self):
        ip = plot(b"PU100,100;PD;AT200,0,300,100;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        points = command[1]
        assert len(points) == 37  # default chord_angle is 5 deg
        assert points[18].isclose((200, 0))
        assert ip.plotter.user_location.isclose((300, 100))

    def test_rel_arc_three_points_clockwise(self):
        ip = plot(b"PU100,100;PD;RT100,100,200,0;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"
        points = command[1]
        assert len(points) == 37  # default chord_angle is 5 deg
        assert points[18].isclose((200, 200))
        assert ip.plotter.user_location.isclose((300, 100))

    def test_polyline_encoded(self):
        ip = plot(b"PE7=U^xGIh;")
        command = get_result(ip.plotter)[0]
        assert command[0] == "Polyline"


class TestTokenizer:
    def parse(self, s: bytes):
        return api.hpgl2_commands(s)

    @pytest.mark.parametrize(
        "s",
        [
            b"%-1BBP;",
            b"%0BBP;",
            b"%1BBP;",
            b"%2BBP;",
            b"%3BBP;",
        ],
    )
    def test_escape(self, s):
        result = self.parse(s)
        assert result[0].name == "BP"

    @pytest.mark.parametrize(
        "s",
        [
            b"IN;PU;PD;",
            b"IN;PU;PD",
            b"INPUPD",
            b"IN PU PD",
            b" INPU PD",
        ],
    )
    def test_short_commands(self, s):
        result = self.parse(s)
        assert len(result) == 3
        assert result[0].name == "IN"
        assert result[1].name == "PU"
        assert result[2].name == "PD"

    @pytest.mark.parametrize(
        "s,i",
        [
            (b"PETEST", 0),
            (b"PUPETEST;PD", 1),
            (b"PUPUPETEST;PD", 2),
        ],
    )
    def test_pe_command(self, s, i):
        result = self.parse(s)
        assert result[i].name == "PE"
        assert result[i].args[0] == b"TEST"

    def test_001(self):
        result = self.parse(b"PA;PA2000,8000")
        assert result[0].name == "PA"
        assert result[1].name == "PA"

    def test_002(self):
        result = self.parse(b"PUSP0PG")
        assert result[0].name == "PU"
        assert result[1].name == "SP"
        assert result[1].args[0] == b"0"
        assert result[2].name == "PG"


class TestPageCoordinates:
    @pytest.fixture(scope="class")
    def page(self):
        page_ = Page(1000, 1000)
        page_.set_ucs(Vec2(500, 500), sx=2, sy=3)
        return page_

    def test_user_to_page_coordinates(self, page):
        assert page.page_point(0, 0).isclose((500, 500))
        assert page.page_point(10, 10).isclose((520, 530))

    def test_user_vector_to_page_vector(self, page):
        assert page.page_vector(0, 0).isclose((0, 0))
        assert page.page_vector(10, 10).isclose((20, 30))

class TestPageAnisotropicScaling:
    def test_isotropic_scaling(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_anisotropic_scaling(-10, 10, -10, 10)
        assert page.user_scaling is True
        assert page.page_point(0, 0).isclose((150, 150))
        assert page.page_point(-10, -10).isclose((100, 100))
        assert page.page_point(10, 10).isclose((200, 200))

    def test_anisotropic_scaling(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_anisotropic_scaling(-10, 10, -20, 20)
        assert page.user_scaling is True
        assert page.page_point(0, 0).isclose((150, 150))
        assert page.page_point(-10, -20).isclose((100, 100))
        assert page.page_point(10, 20).isclose((200, 200))

    def test_reverse_anisotropic_scaling(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        # reverse x and y axis:
        page.set_anisotropic_scaling(10, -10, 20, -20)
        assert page.user_scaling is True
        assert page.page_point(0, 0).isclose((150, 150))
        assert page.page_point(10, 20).isclose((100, 100))
        assert page.page_point(-10, -20).isclose((200, 200))

class TestPageIsotropicScaling:
    def test_isotropic_bottom_window_50(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 20, 0, 10)
        assert page.user_scaling is True
        assert page.page_point(0, 0).isclose((100, 125))
        assert page.page_point(10, 5).isclose((150, 150))
        assert page.page_point(20, 10).isclose((200, 175))

    def test_isotropic_bottom_window_0(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 20, 0, 10, 0, 0)
        assert page.page_point(0, 0).isclose((100, 100))
        assert page.page_point(10, 5).isclose((150, 125))
        assert page.page_point(20, 10).isclose((200, 150))

    def test_isotropic_bottom_window_100(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 20, 0, 10, 1, 1)
        assert page.page_point(0, 0).isclose((100, 150))
        assert page.page_point(10, 5).isclose((150, 175))
        assert page.page_point(20, 10).isclose((200, 200))

    def test_isotropic_left_window_50(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 10, 0, 20)
        assert page.page_point(0, 0).isclose((125, 100))
        assert page.page_point(5, 10).isclose((150, 150))
        assert page.page_point(10, 20).isclose((175, 200))

    def test_isotropic_left_window_0(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 10, 0, 20, 0, 0)
        assert page.page_point(0, 0).isclose((100, 100))
        assert page.page_point(5, 10).isclose((125, 150))
        assert page.page_point(10, 20).isclose((150, 200))

    def test_isotropic_left_window_100(self):
        page = Page(1000, 1000)
        page.set_scaling_points(Vec2(100, 100), Vec2(200, 200))
        page.set_isotropic_scaling(0, 10, 0, 20, 1, 1)
        assert page.page_point(0, 0).isclose((150, 100))
        assert page.page_point(5, 10).isclose((175, 150))
        assert page.page_point(10, 20).isclose((200, 200))

def test_arc_angles():
    from ezdxf.addons.hpgl2.plotter import arc_angles

    angles = list(arc_angles(0, 360, 5))
    assert len(angles) == 73
    assert angles[-1] == pytest.approx(360)

    angles = list(arc_angles(0, -360, 5))
    assert len(angles) == 73
    assert angles[-1] == pytest.approx(-360)


def test_sweeping_angle():
    from ezdxf.addons.hpgl2.plotter import sweeping_angle

    assert sweeping_angle(0, 45, 90) == 90
    assert sweeping_angle(90, 45, 0) == -90
    assert sweeping_angle(330, 0, 30) == 60
    assert sweeping_angle(330, 180, 30) == -300
    assert sweeping_angle(30, 0, 330) == -60
    assert sweeping_angle(30, 180, 330) == 300


if __name__ == "__main__":
    pytest.main([__file__])
