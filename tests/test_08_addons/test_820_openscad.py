#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import openscad
from ezdxf.render import MeshBuilder
from ezdxf.math import Matrix44, Vec3


def test_matrix44_to_multmatrix_str():
    s = openscad.str_matrix44(Matrix44.translate(20, 30, 40))
    assert (
        s == "[[1.0, 0.0, 0.0, 20.0],"
        " [0.0, 1.0, 0.0, 30.0],"
        " [0.0, 0.0, 1.0, 40.0],"
        " [0.0, 0.0, 0.0, 1.0]]"
    )


class TestScriptBuilder:
    def test_build_boolean_operation(self):
        m = MeshBuilder()
        script = openscad.boolean_operation(openscad.UNION, m, m)
        assert script == (
            "union() {\n"
            "polyhedron(points = [\n"
            "], faces = [\n"
            "], convexity = 10);\n"
            "\n"
            "polyhedron(points = [\n"
            "], faces = [\n"
            "], convexity = 10);\n"
            "\n"
            "}"
        )

    @pytest.mark.parametrize(
        "op,func",
        [
            (openscad.UNION, "union()"),
            (openscad.DIFFERENCE, "difference()"),
            (openscad.INTERSECTION, "intersection()"),
        ],
    )
    def test_build_all_operations(self, op, func):
        m = MeshBuilder()
        assert openscad.boolean_operation(op, m, m).startswith(func)

    def test_add_multmatrix_operation(self):
        script = openscad.Script()
        script.add_multmatrix(Matrix44.translate(20, 30, 40))
        result = script.get_string()
        assert result.startswith("multmatrix(m = [[")
        assert result.endswith("]])"), "operation without a pending ';'"

    def test_add_translation_operation(self):
        script = openscad.Script()
        script.add_translate((10, 20, 30))
        assert script.get_string() == "translate(v = [10, 20, 30])"

    def test_add_rotation_operation(self):
        script = openscad.Script()
        script.add_rotate(10, 20, 30)
        assert script.get_string() == "rotate(a = [10, 20, 30])"

    def test_add_rotation_about_axis_operation(self):
        script = openscad.Script()
        script.add_rotate_about_axis(40, (10, 20, 30))
        assert script.get_string() == "rotate(a = 40, v = [10, 20, 30])"

    def test_add_scale_operation(self):
        script = openscad.Script()
        script.add_scale(10, 20, 30)
        assert script.get_string() == "scale(v = [10, 20, 30])"

    def test_add_resize_operation(self):
        script = openscad.Script()
        script.add_resize(10, 20, 30)
        assert script.get_string() == "resize(newsize = [10, 20, 30])"

    def test_add_auto_resize_operation(self):
        script = openscad.Script()
        script.add_resize(10, 0, 0, auto=True)
        assert (
            script.get_string() == "resize(newsize = [10, 0, 0], auto = true)"
        )

    def test_add_multi_auto_resize_operation(self):
        script = openscad.Script()
        script.add_resize(10, 0, 0, auto=(False, True, False))
        assert (
            script.get_string()
            == "resize(newsize = [10, 0, 0], auto = [false, true, false])"
        )

    def test_add_mirror_operation(self):
        script = openscad.Script()
        script.add_mirror((10, 0, 0))
        assert script.get_string() == "mirror(v = [1, 0, 0])"


if __name__ == "__main__":
    pytest.main([__file__])
