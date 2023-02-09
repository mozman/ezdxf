from pathlib import Path
import ezdxf

DIR = Path("~/Desktop/Outbox").expanduser()
doc = ezdxf.new()
msp = doc.modelspace()

hatch = msp.add_hatch(color=1)

# 1. polyline path
hatch.paths.add_polyline_path(
    [
        (240, 210, 0),
        (0, 210, 0),
        (0, 0, 0.0),
        (240, 0, 0),
    ],
    is_closed=1,
    flags=ezdxf.const.BOUNDARY_PATH_EXTERNAL,
)
# 2. edge path
edge_path = hatch.paths.add_edge_path(flags=ezdxf.const.BOUNDARY_PATH_OUTERMOST)
edge_path.add_spline(
    control_points=[
        (126.658105895725, 177.0823706957212),
        (141.5497003747484, 187.8907860433995),
        (205.8997365206943, 154.7946313459515),
        (113.0168862297068, 117.8189380884978),
        (202.9816918983783, 63.17222935389572),
        (157.363511042264, 26.4621294342132),
        (144.8204003260554, 28.4383294369643),
    ],
    knot_values=[
        0.0,
        0.0,
        0.0,
        0.0,
        55.20174685732758,
        98.33239645153571,
        175.1126541251052,
        213.2061566683142,
        213.2061566683142,
        213.2061566683142,
        213.2061566683142,
    ],
)
edge_path.add_arc(
    center=(152.6378550678883, 128.3209356351659),
    radius=100.1880612627354,
    start_angle=94.4752130054052,
    end_angle=177.1345242028005,
)
edge_path.add_line(
    (52.57506282464041, 123.3124200796114),
    (126.658105895725, 177.0823706957212),
)

doc.saveas(DIR / "edge_path_hatch.dxf")
