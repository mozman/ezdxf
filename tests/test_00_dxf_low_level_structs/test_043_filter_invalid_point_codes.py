# Copyright (c) 2019 Manfred Moitzi
# License: MIT License


from ezdxf.lldxf.repair import filter_invalid_point_codes


def test_invalid_y_coord_after_xyz():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (30, 3), (20, 0)]
    ))
    assert result == [(10, 1), (20, 2), (30, 3)]


def test_invalid_y_coord_after_xy():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (21, 2)]
    ))
    assert result == [(10, 1), (20, 2)]


def test_z_axis_after_valid_point():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (30, 3), (30, 0)]
    ))
    assert result == [(10, 1), (20, 2), (30, 3)]


def test_misplaced_z_axis():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (1, 'Text'), (30, 0), (1, 'xxx')]
    ))
    assert result == [(10, 1), (20, 2), (1, 'Text'), (1, 'xxx')]


def test_correct_xy_axis():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (10, 1), (20, 0)]
    ))
    assert result == [(10, 1), (20, 2), (10, 1), (20, 0)]


def test_invalid_single_x_axis():
    result = list(filter_invalid_point_codes(
        [(10, 1), (20, 2), (10, 1)]
    ))
    assert result == [(10, 1), (20, 2)]


