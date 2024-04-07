# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities import Insert, Body
from ezdxf.layouts import Modelspace
from ezdxf.math import Matrix44, Vec3
from ezdxf.protocols import SupportsTemporaryTransformation


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new("R2007")
    return doc.modelspace()


@pytest.fixture()
def body(msp: Modelspace):
    return msp.add_body()


def test_supports_temporary_transform(body: Body):
    assert isinstance(body, SupportsTemporaryTransformation) is True


def test_add_and_get_transform(body: Body):
    m = Matrix44.translate(10, 20, 30)
    tt = body.temporary_transformation()
    tt.set_matrix(m)

    tt2 = body.temporary_transformation()
    m2 = tt2.get_matrix()
    assert isinstance(m2, Matrix44)

    v = Vec3(1, 1, 1)
    assert m.transform(v).isclose(m2.transform(v))


def test_apply_temp_transform(body: Body, msp: Modelspace):
    m = Matrix44.translate(10, 20, 30)
    tt = body.temporary_transformation()
    tt.set_matrix(m)

    done = tt.apply_transformation(body)
    assert done is True

    # BODY was replaced by a block reference to an anonymous block
    insert = msp[-1]
    assert isinstance(insert, Insert)
    assert insert.dxf.name.startswith("*U")
    assert insert.dxf.insert.isclose((10, 20, 30))

    # anonymous block contains BODY
    block = insert.block()
    assert block is not None
    assert block[0] is body


def test_transform_and_copy(body: Body):
    m = Matrix44.translate(10, 20, 30)
    tt = body.temporary_transformation()
    tt.set_matrix(m)

    copy = body.copy()
    tt2 = copy.temporary_transformation()
    m2 = tt2.get_matrix()
    assert isinstance(m2, Matrix44)

    v = Vec3(1, 1, 1)
    assert m.transform(v).isclose(m2.transform(v))


if __name__ == "__main__":
    pytest.main([__file__])
