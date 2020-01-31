from pathlib import Path
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()
doc = ezdxf.new()
msp = doc.modelspace()

# Create base geometry
lwpolyline = msp.add_lwpolyline(
    [(0, 0, 0), (10, 0, .5), (10, 10, 0), (0, 10, 0)],
    format='xyb',
    dxfattribs={'closed': True},
)

hatch = msp.add_hatch(color=2)
path = hatch.paths.add_polyline_path(
    # get path vertices from associated LWPOLYLINE entity
    lwpolyline.get_points(format='xyb'),
    # get closed state also from associated LWPOLYLINE entity
    is_closed=lwpolyline.closed,
)

# Set association between boundary path and LWPOLYLINE
hatch.associate(path, [lwpolyline])


doc.saveas(DIR / 'hatch_assoc_polyline_path.dxf')
