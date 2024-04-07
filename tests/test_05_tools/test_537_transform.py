#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import math

import ezdxf
from ezdxf import transform
from ezdxf.layouts import VirtualLayout


class TestInplaceMethod:
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
        log = transform.inplace(msp, m)
        assert len(log) == 0
        point = msp[0]
        assert point.dxf.location.isclose((1, 2, 0))
        text = msp[1]
        assert text.dxf.insert.isclose((1, 2, 0))
        circle = msp[2]
        assert circle.dxf.center.isclose((1, 2, 0))

    @pytest.mark.parametrize("msp", ["doc"], indirect=True)
    def test_non_uniform_transformation(self, msp):
        # not supported by virtual layouts
        m = transform.Matrix44.scale(1, 2, 1)
        log = transform.inplace(msp, m)
        assert len(log) == 0
        entity = msp[2]
        assert entity.dxftype() == "ELLIPSE"

    def test_entities_without_transformation_support(self):
        from ezdxf.entities import Layer

        m = transform.Matrix44.translate(1, 0, 0)
        log = transform.inplace([Layer.new()], m)
        assert log[0].error == transform.Error.TRANSFORMATION_NOT_SUPPORTED

    def test_acis_entities(self):
        # new in v1.3.0: ACIS entities support a temporary transformation
        #
        # This way a temporary transformation of ACIS entities is stored by ezdxf.
        # This temp. transformation has to be applied before export otherwise a warning 
        # will be logged.

        msp = VirtualLayout()
        body = msp.add_body()  # ACIS entity
        m = transform.Matrix44.translate(1, 2, 3)
        log = transform.inplace(msp, m)
        assert len(log) == 0

        m2 = body.temporary_transformation().get_matrix()
        v = (3, 2, 1)
        assert m.transform(v).isclose(m2.transform(v))


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

    def test_scale(self, msp):
        transform.scale(msp, sx=2, sy=3, sz=4)
        point = msp[0]
        assert point.dxf.location.isclose((2, 3, 4))

    def test_z_rotate(self, msp):
        transform.z_rotate(msp, angle=math.pi / 2)
        point = msp[0]
        assert point.dxf.location.isclose((-1, 1, 1))

    def test_y_rotate(self, msp):
        transform.y_rotate(msp, angle=math.pi / 2)
        point = msp[0]
        assert point.dxf.location.isclose((1, 1, -1))

    def test_x_rotate(self, msp):
        transform.x_rotate(msp, angle=math.pi / 2)
        point = msp[0]
        assert point.dxf.location.isclose((1, -1, 1))


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
        log, entities = transform.copies(msp, m=transform.Matrix44.scale(2, 3, 1))
        assert len(log) == 0
        assert entities[0].dxftype() == "ELLIPSE"
        assert entities[1].dxftype() == "POINT"

    def test_scale_virtual_polyline_with_bulge_non_uniform(self):
        layout = VirtualLayout()
        layout.add_lwpolyline([(-1, 0, 0, 0, 1), (1, 0)])

        log, entities = transform.copies(layout, m=transform.Matrix44.scale(2, 3, 1))
        assert len(log) == 0
        assert len(entities) == 1
        assert entities[0].dxftype() == "ELLIPSE"


class TestMLeaderNonUniformScaling:
    @pytest.fixture(scope="class")
    def msp(self):
        from ezdxf.render import mleader
        from ezdxf.math import Vec2

        doc = ezdxf.new()
        msp = doc.modelspace()
        ml_builder = msp.add_multileader_mtext("Standard")
        ml_builder.set_content("Line1\nLine2")
        ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, 15)])
        ml_builder.build(insert=Vec2(5, 0))
        return msp

    def test_transformation_will_not_be_applied_inplace(self, msp):
        log = transform.scale(msp, 2, 3, 1)
        assert log[0].error == transform.Error.NON_UNIFORM_SCALING_ERROR
        assert msp[0].dxftype() == "MULTILEADER"

    def test_mleader_will_not_copied(self, msp):
        log, clones = transform.copies(msp, m=transform.Matrix44.scale(2, 3, 1))
        assert log[0].error == transform.Error.NON_UNIFORM_SCALING_ERROR
        assert len(clones) == 0


if __name__ == "__main__":
    pytest.main([__file__])
