#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import meshex


class TestStlLoader:
    def test_empty_file_returns_empty_mesh(self):
        mesh = meshex.stl_loads("")
        assert len(mesh.vertices) == 0

    def test_load_a_single_face(self):
        """This is the minimum required format accuracy the parser needs"""
        mesh = meshex.stl_loads(
            "vertex 0 0 0\nvertex 1 0 0\nvertex 1 1 0\nendloop\n"
        )
        assert mesh.vertices[0] == (0, 0, 0)
        assert mesh.vertices[1] == (1, 0, 0)
        assert mesh.vertices[2] == (1, 1, 0)
        assert mesh.faces[0] == (0, 1, 2)

    def test_parsing_error_too_few_axis(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0 0")

    def test_parsing_error_invalid_coordinate_format(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0, 0, 0")

    def test_parsing_error_invalid_floats(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0 0 z")


if __name__ == "__main__":
    pytest.main([__file__])
