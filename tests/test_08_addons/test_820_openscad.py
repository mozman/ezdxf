#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import openscad
from ezdxf.render import MeshBuilder
from ezdxf.math import Matrix44


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

    def test_adding_multmatrix_operation(self):
        script = openscad.Script()
        script.add_multmatrix(Matrix44.translate(20, 30, 40))
        result = script.get_string()
        assert result.startswith("multmatrix(m = [[")
        assert result.endswith("]])"), "operation without a pending ';'"


if __name__ == "__main__":
    pytest.main([__file__])
