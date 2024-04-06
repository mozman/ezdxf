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
    body.add_temporary_transformation(m)

    m2 = body.get_temporary_transformation()
    assert isinstance(m2, Matrix44)

    v = Vec3(1, 1, 1)
    assert m.transform(v).isclose(m2.transform(v))


def test_apply_temp_transform(body: Body, msp: Modelspace):
    m = Matrix44.translate(10, 20, 30)
    body.add_temporary_transformation(m)
    done = body.apply_temporary_transformation()
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


if __name__ == "__main__":
    pytest.main([__file__])
