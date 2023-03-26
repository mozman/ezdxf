#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf import transform
from ezdxf.layouts import VirtualLayout


class TestMatrixMethod:
    """The tests do not check if all possible transformations will be performed correct,
    this is done by the tests for the transform() method of the entities.
    """

    @pytest.fixture
    def msp(self, request):
        if request.param == "doc":
            doc = ezdxf.new()
            msp = doc.modelspace()
        elif request.param == "virtual":
            # The matrix() function supports virtual entities as well.
            msp = VirtualLayout()
        else:
            return ValueError(request.param)
        msp.add_point((0, 0))
        msp.add_text("TEXT")
        msp.add_circle((0, 0), radius=1)
        return msp

    @pytest.mark.parametrize("msp", ["doc", "virtual"], indirect=True)
    def test_transformation_by_matrix_without_errors(self, msp):
        m = transform.Matrix44.translate(1, 2, 0)
        log = transform.matrix(msp, m)
        assert len(log) == 0
        point = msp[0]
        assert point.dxf.location.isclose((1, 2, 0))
        text = msp[1]
        assert text.dxf.insert.isclose((1, 2, 0))
        circle = msp[2]
        assert circle.dxf.center.isclose((1, 2, 0))

    @pytest.mark.parametrize("msp", ["doc", "virtual"], indirect=True)
    def test_non_uniform_transformation(self, msp):
        m = transform.Matrix44.scale(1, 2, 1)
        log = transform.matrix(msp, m)
        assert len(log) == 1
        entry = log[0]
        assert entry.entity.dxftype() == "CIRCLE"

    def test_entities_without_transformation_support(self):
        from ezdxf.entities import Layer

        m = transform.Matrix44.translate(1, 0, 0)
        log = transform.matrix([Layer.new()], m)
        assert log[0].error == transform.Error.TRANSFORMATION_NOT_SUPPORTED

    def test_acis_entities(self):
        # ACIS entities do not have transformation support yet, but maybe in the future!
        msp = VirtualLayout()
        msp.add_body()  # ACIS entity
        m = transform.Matrix44.translate(1, 0, 0)
        log = transform.matrix(msp, m)
        assert log[0].error == transform.Error.TRANSFORMATION_NOT_SUPPORTED


class TestConvenientFunctions:
    @pytest.fixture
    def msp(self):
        msp = VirtualLayout()
        msp.add_point((1, 1, 1))
        return msp

    def test_translate(self, msp):
        transform.translate(msp, offset=(1, 2))
        point = msp[0]
        assert point.dxf.location.isclose((2, 3, 1))

    def test_scale_uniform(self, msp):
        transform.scale_uniform(msp, factor=2)
        point = msp[0]
        assert point.dxf.location.isclose((2, 2, 2))


def test_circle_non_uniform_scaling():
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_circle((0, 0), radius=1)
    transform.scale(msp, sx=3, sy=2, sz=1)

    ellipse = msp[0]
    assert ellipse.dxftype() == "ELLIPSE"
    assert ellipse.dxf.center.isclose((0, 0, 0))
    assert ellipse.dxf.major_axis.isclose((3, 0, 0))
    assert ellipse.dxf.ratio == pytest.approx(0.6666666)


def test_polyline_non_uniform_scaling():
    doc = ezdxf.new()
    msp = doc.modelspace()
    # semi-circle: center=(0, 0); radius=1
    msp.add_lwpolyline([(-1, 0, 0, 0, 1), (1, 0)])
    transform.scale(msp, sx=3, sy=2, sz=1)

    ellipse = msp[0]
    assert ellipse.dxftype() == "ELLIPSE"
    assert ellipse.dxf.center.isclose((0, 0, 0))
    assert ellipse.dxf.major_axis.isclose((3, 0, 0))
    assert ellipse.dxf.ratio == pytest.approx(0.6666666)


def test_virtual_entities_do_not_support_non_uniform_scaling():
    msp = VirtualLayout()
    msp.add_circle((0, 0), radius=1)
    log = transform.scale(msp, sx=3, sy=2, sz=1)

    # does not transform the CIRCLE
    circle = msp[0]
    assert circle.dxftype() == "CIRCLE"
    assert circle.dxf.radius == pytest.approx(1.0)

    assert len(log) == 1
    assert log[0].error == transform.Error.VIRTUAL_ENTITY_NOT_SUPPORTED


class TestVirtualCopies:
    @pytest.fixture
    def msp(self):
        msp = VirtualLayout()
        msp.add_circle((0, 0), radius=1)
        msp.add_point((1, 1, 1))
        return msp

    def test_just_copy(self, msp):
        log, entities = transform.copies(msp)
        assert len(entities) == 2
        assert all(e.is_virtual for e in entities)

    def test_scale_virtual_circular_arcs_non_uniform(self, msp):
        log, entities = transform.copies(
            msp, m=transform.Matrix44.scale(2, 3, 1)
        )
        assert len(log) == 0
        assert entities[0].dxftype() == "ELLIPSE"
        assert entities[1].dxftype() == "POINT"

    def test_scale_virtual_polyline_with_bulge_non_uniform(self):
        layout = VirtualLayout()
        layout.add_lwpolyline([(-1, 0, 0, 0, 1), (1, 0)])

        log, entities = transform.copies(
            layout, m=transform.Matrix44.scale(2, 3, 1)
        )
        assert len(log) == 0
        assert len(entities) == 1
        assert entities[0].dxftype() == "ELLIPSE"


if __name__ == "__main__":
    pytest.main([__file__])
