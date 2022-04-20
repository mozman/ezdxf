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


OFF_VALID_1 = """OFF
# just a comment
8 6 0
-0.500000 -0.500000 0.500000  #  ignor this
0.500000 -0.500000 0.500000
-0.500000 0.500000 0.500000
0.500000 0.500000 0.500000
-0.500000 0.500000 -0.500000
0.500000 0.500000 -0.500000
-0.500000 -0.500000 -0.500000
0.500000 -0.500000 -0.500000
4 0 1 3 2  # ignore this
4 2 3 5 4
4 4 5 7 6
4 6 7 1 0
4 1 7 5 3
4 6 0 2 4
"""

OFF_VALID_2 = """OFF 8 6 0  # ignore this
-0.500000 -0.500000 0.500000  #  ignore this
0.500000 -0.500000 0.500000
-0.500000 0.500000 0.500000
0.500000 0.500000 0.500000
-0.500000 0.500000 -0.500000
0.500000 0.500000 -0.500000
-0.500000 -0.500000 -0.500000
0.500000 -0.500000 -0.500000
4 0 1 3 2  # ignore this
4 2 3 5 4
4 4 5 7 6
4 6 7 1 0
4 1 7 5 3
4 6 0 2 4


# ignore this
"""


class TestOFFLoader:
    @pytest.mark.parametrize("data", [OFF_VALID_1, OFF_VALID_2])
    def test_valid_data(self, data):
        mesh = meshex.off_loads(data)
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 6

    def test_minimal_data(self):
        mesh = meshex.off_loads("3 1 0\n0 0 0\n 0 1 0\n1 1 0\n3 0 1 2")
        assert len(mesh.vertices) == 3
        assert len(mesh.faces) == 1

    @pytest.mark.parametrize(
        "data",
        [
            "",  # no data
            "OFF",  # no data
            "OFF 8 6 0",  # invalid data count
            "OFF 8 6 0\n1 2 3",  # invalid data count
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 Z\n3 0 1 2\n ",  # vertex parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0\n3 0 1 2\n ",  # vertex parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 0\n3 0 1\n ",  # face parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 0\n3 0 1 z\n ",  # face parsing error
        ],
    )
    def test_parsing_error_invalid_data_raises_parsing_error(self, data):
        with pytest.raises(meshex.ParsingError):
            meshex.off_loads(data)


if __name__ == "__main__":
    pytest.main([__file__])
