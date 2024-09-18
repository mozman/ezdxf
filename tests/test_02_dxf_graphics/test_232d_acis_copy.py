# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.math import Matrix44
from ezdxf.layouts import Modelspace

SAT = ("INVALID", "DUMMY", "SAT", "DATA")
SAB = b"INVALID_DUMMY_SAB_DATA"


class TestCopySAT:
    @pytest.fixture(scope="module")
    def msp(self):
        doc = ezdxf.new("R2007")  # SAT
        return doc.modelspace()

    def test_copy_body(self, msp: Modelspace):
        body = msp.add_body()
        body.sat = SAT
        copy = body.copy()
        assert copy.sat is SAT

    def test_copy_region(self, msp: Modelspace):
        region = msp.add_region()
        region.sat = SAT
        copy = region.copy()
        assert copy.sat is SAT

    def test_copy_3dsolid(self, msp: Modelspace):
        solid3d = msp.add_3dsolid()
        solid3d.dxf.history_handle = "FEFE"
        solid3d.sat = SAT

        copy = solid3d.copy()
        # copy history handle? so far the entities have the same history
        assert copy.dxf.history_handle == "FEFE"
        assert copy.sat == SAT

    def test_copy_extruded_surface(self, msp: Modelspace):
        extruded_surface = msp.add_extruded_surface()
        extruded_surface.sat = SAT
        m = Matrix44()
        extruded_surface.transformation_matrix_extruded_entity = m
        extruded_surface.sweep_entity_transformation_matrix = m
        extruded_surface.path_entity_transformation_matrix = m

        copy = extruded_surface.copy()
        assert copy.sat == SAT

        # Matrix44 instances are mutable and must be copied!
        assert copy.transformation_matrix_extruded_entity is not m
        assert copy.sweep_entity_transformation_matrix is not m
        assert copy.path_entity_transformation_matrix is not m

    def test_copy_lofted_surface(self, msp: Modelspace):
        lofted_surface = msp.add_lofted_surface()
        lofted_surface.sat = SAT
        m = Matrix44()
        lofted_surface.transformation_matrix_lofted_entity = m

        copy = lofted_surface.copy()
        assert copy.sat == SAT

        # Matrix44 instances are mutable and must be copied!
        assert copy.transformation_matrix_lofted_entity is not m

    def test_copy_revolved_surface(self, msp: Modelspace):
        revolved_surface = msp.add_revolved_surface()
        revolved_surface.sat = SAT
        m = Matrix44()
        revolved_surface.transformation_matrix_revolved_entity = m

        copy = revolved_surface.copy()
        assert copy.sat == SAT

        # Matrix44 instances are mutable and must be copied!
        assert copy.transformation_matrix_revolved_entity is not m

    def test_copy_swept_surface(self, msp: Modelspace):
        swept_surface = msp.add_swept_surface()
        swept_surface.sat = SAT
        m = Matrix44()
        swept_surface.transformation_matrix_sweep_entity = m
        swept_surface.transformation_matrix_path_entity = m
        swept_surface.sweep_entity_transformation_matrix = m
        swept_surface.path_entity_transformation_matrix = m
        swept_surface.dxf.swept_entity_id = 1234
        swept_surface.dxf.path_entity_id = 5678

        copy = swept_surface.copy()
        assert copy.sat == SAT
        # copy references the same base geometries
        assert copy.dxf.swept_entity_id == 1234
        assert copy.dxf.path_entity_id == 5678

        # Matrix44 instances are mutable and must be copied!
        assert copy.transformation_matrix_sweep_entity is not m
        assert copy.transformation_matrix_path_entity is not m
        assert copy.sweep_entity_transformation_matrix is not m
        assert copy.path_entity_transformation_matrix is not m


class TestCopySAB:
    @pytest.fixture(scope="module")
    def msp(self):
        doc = ezdxf.new("R2013")  # SAT
        return doc.modelspace()

    def test_copy_body(self, msp: Modelspace):
        body = msp.add_body()
        body.sab = SAB
        copy = body.copy()
        assert copy.sab == SAB
        assert isinstance(copy.dxf.uid, str) is True
        assert copy.dxf.uid != body.dxf.uid


if __name__ == "__main__":
    pytest.main([__file__])
