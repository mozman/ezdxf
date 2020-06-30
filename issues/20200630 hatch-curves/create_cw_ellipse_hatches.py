from pathlib import Path
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

# ellipse is the same quirks:
hatch = msp.add_hatch(color=1)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (0, 0.5))
ep.add_ellipse(
    center=(0, 0),
    major_axis=(1, 0),
    ratio=0.5,
    start_angle=270,  # 360 - 90
    end_angle=360,  # 360 - 0
    ccw=False,
)
ep.add_line((1, 0), (0, 0))
hatch.translate(0.25, 0.25, 0)

hatch = msp.add_hatch(color=2)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (-1, 0))
ep.add_ellipse(
    center=(0, 0),
    major_axis=(1, 0),
    ratio=0.5,
    start_angle=180,  # 360 -180
    end_angle=270,  # 360 - 90
    ccw=False,
)
ep.add_line((0, .5), (0, 0))
hatch.translate(-0.25, 0.25, 0)

hatch = msp.add_hatch(color=3)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (0, -0.5))
ep.add_ellipse(
    center=(0, 0),
    major_axis=(1, 0),
    ratio=0.5,
    start_angle=90,  # 360 - 270
    end_angle=180,  # 360 - 180
    ccw=False,
)
ep.add_line((-1, 0), (0, 0))
hatch.translate(-0.25, -0.25, 0)

hatch = msp.add_hatch(color=4)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (1, 0))
ep.add_ellipse(
    center=(0, 0),
    major_axis=(1, 0),
    ratio=0.5,
    start_angle=360,  # 360 - 0
    end_angle=90,  # 360 - 270
    ccw=False,
)
ep.add_line((0, -0.5), (0, 0))
hatch.translate(0.25, -0.25, 0)


doc.set_modelspace_vport(height=5)
doc.saveas(DIR / 'cw_ellipse_hatch.dxf')
