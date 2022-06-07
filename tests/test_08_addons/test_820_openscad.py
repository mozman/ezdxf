#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import openscad
from ezdxf.render import MeshBuilder


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

    @pytest.mark.parametrize("op,func", [
        (openscad.UNION, "union()"),
        (openscad.DIFFERENCE, "difference()"),
        (openscad.INTERSECTION, "intersection()"),
    ])
    def test_build_all_operations(self, op, func):
        m = MeshBuilder()
        assert openscad.boolean_operation(op, m, m).startswith(func)


if __name__ == "__main__":
    pytest.main([__file__])
