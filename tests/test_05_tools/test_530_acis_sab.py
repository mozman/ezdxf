#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from datetime import datetime
from ezdxf import acis
from ezdxf.acis import sab, parsing

T = sab.Tags


def test_decode_header(sab0):
    decoder = sab.Decoder(sab0)
    header = decoder.read_header()
    assert header.version == 21800
    assert header.n_records == 0
    assert header.n_entities == 2
    assert header.flags == 12
    assert header.product_id == "Open Design Alliance ACIS Builder"
    assert header.acis_version == "ACIS 218.00 NT"
    assert header.creation_date == datetime(2022, 5, 2, 18, 54, 43)
    assert header.units_in_mm == 1.0


def test_decode_first_record(sab0):
    decoder = sab.Decoder(sab0)
    _ = decoder.read_header()
    record = decoder.read_record()
    assert record == [
        (T.ENTITY_TYPE, "asmheader"),
        (T.POINTER, -1),
        (T.INT, -1),
        (T.STR, "208.0.4.7009"),
    ]


def test_decode_all_records(sab0):
    decoder = sab.Decoder(sab0)
    _ = decoder.read_header()
    records = list(decoder.read_records())
    assert len(records) == 88
    assert records[-1][0].value == "End-of-ASM-data"


def test_parse_sab(sab0):
    builder = sab.parse_sab(sab0)
    assert builder.header.version == 21800
    assert len(builder.entities) == 88
    assert builder.entities[0].name == "asmheader"
    assert builder.entities[-1].name == "End-of-ASM-data"


class TestSabEntity:
    @pytest.fixture(scope="class")
    def builder(self, sab0):
        return sab.parse_sab(sab0)

    @pytest.fixture(scope="class")
    def body(self, builder):
        return builder.bodies[0]

    def test_get_pointer_at_index(self, body):
        assert body.name == "body"
        assert body.attributes.is_null_ptr is True

    def test_find_first_entity(self, body):
        assert body.find_first("lump").name == "lump"

    def test_find_first_returns_null_ptr_if_not_found(self, body):
        assert body.find_first("vertex").is_null_ptr is True

    def test_query_entities(self, builder):
        points = list(builder.query(lambda e: e.name == "point"))
        assert len(points) == 8

    def test_find_entities_in_nodes(self, body):
        face = body.find_first("lump").find_first("shell").find_first("face")
        assert face.name == "face"

    def test_find_entities_in_path(self, body):
        face = body.find_path("lump/shell/face")
        assert face.name == "face"

    def test_find_in_invalid_path_return_null_pointer(self, body):
        face = body.find_path("lump/xxx/face")
        assert face.is_null_ptr is True

    def test_find_all(self, builder):
        coedge = builder.entities[12]
        assert len(coedge.find_all("coedge")) == 3


def ptr_token(v: sab.SabEntity):
    return sab.Token(T.POINTER, v)


def int_token(v: int):
    return sab.Token(T.INT, v)


def dbl_token(v: float):
    return sab.Token(T.DOUBLE, float(v))


def str_token(v: str, t=T.STR):
    return sab.Token(t, v)


def bool_token(v: bool):
    return sab.Token(T.BOOL_TRUE if v else T.BOOL_FALSE, v)


class TestParseValues:
    @pytest.fixture
    def null(self):
        return ptr_token(sab.NULL_PTR)

    def test_parse_integers(self, null):
        data = [null, int_token(1), int_token(2), null]
        assert sab.parse_values([], "i") == []
        assert sab.parse_values(data, "i") == [1]
        assert sab.parse_values(data, "i;i") == [1, 2]
        assert sab.parse_values(data, "i;i;i") == [1, 2]

    def test_parse_vec3(self, null):
        loc_vec = sab.Token(T.LOCATION_VEC, (1.0, 2.0, 3.0))
        dir_vec = sab.Token(T.DIRECTION_VEC, (0.0, 0.0, 1.0))
        data = [null, loc_vec, dir_vec, null]
        assert sab.parse_values([], "v") == []
        assert sab.parse_values(data, "v") == [(1, 2, 3)]
        assert sab.parse_values(data, "v;v") == [(1, 2, 3), (0, 0, 1)]

    def test_parse_floats(self, null):
        data = [null, dbl_token(1), dbl_token(2), null]
        assert sab.parse_values([], "f") == []
        assert sab.parse_values(data, "f") == [1.0]
        assert sab.parse_values(data, "f;f") == [1.0, 2.0]
        assert sab.parse_values(data, "f;f;f") == [1.0, 2.0]

    def test_parse_unbounded_values(self, null):
        """Unbounded values "I" are represented in SAB by the BOOL_TRUE token."""
        data = [null, bool_token(True), null]
        assert sab.parse_values(data, "f") == [
            float("inf")
        ], "should be translated to infinity"

    def test_parse_boolean(self, null):
        data = [null, bool_token(True), bool_token(False), null]
        assert sab.parse_values([], "b") == []
        assert sab.parse_values(data, "b") == [True]
        assert sab.parse_values(data, "b;b") == [True, False]

    def test_parse_user_strings(self, null):
        data = [null, str_token("usr1"), str_token("usr2", T.LITERAL_STR), null]
        assert sab.parse_values([], "@") == []
        assert sab.parse_values(data, "@") == ["usr1"]
        assert sab.parse_values(data, "@;@") == ["usr1", "usr2"]
        assert sab.parse_values(data, "@;@;@") == ["usr1", "usr2"]

    def test_parse_mixed_values(self):
        data = [dbl_token(1), str_token("usr1"), bool_token(True)]
        assert sab.parse_values(data, "f;@;b") == [1.0, "usr1", True]

    def test_value_order_must_match(self):
        data = [str_token("not_a_float")]
        with pytest.raises(sab.ParsingError):
            sab.parse_values(data, "f;f")

    def test_skip_unknown_values(self):
        data = [int_token(7), str_token("not_a_float"), dbl_token(1)]
        assert sab.parse_values(data, "i;?;f") == [7, 1.0]

    def test_ignore_entities_between_values(self, null):
        data = [int_token(7), null, dbl_token(1)]
        assert sab.parse_values(data, "i;f") == [7, 1.0]


def test_parse_body_polygon_faces(sab0):
    builder = sab.parse_sab(sab0)
    lumps = list(parsing.body_planar_polygon_faces(builder.bodies[0]))
    assert len(lumps) == 1
    faces = lumps[0]
    assert len(faces) == 6


def test_body_to_mesh(sab0):
    builder = sab.parse_sab(sab0)
    meshes = acis.body_to_mesh(builder.bodies[0])
    assert len(meshes) == 1
    mesh = meshes[0]
    assert len(mesh.faces) == 6
    assert len(mesh.vertices) == 8


if __name__ == "__main__":
    pytest.main([__file__])
