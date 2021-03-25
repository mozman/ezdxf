from pathlib import Path
OUTDIR = Path('~/Desktop/Outbox').expanduser()

import ezdxf

doc = ezdxf.new('R2000')
doc.set_modelspace_vport(15, center=(5, 5))
msp = doc.modelspace()

hatch = msp.add_hatch(color=1, dxfattribs={
    'hatch_style': 0,
    # 0 = nested
    # 1 = outer
    # 2 = ignore
})

# The first path has to set flag: 1 = external
# flag const.BOUNDARY_PATH_POLYLINE is added (OR) automatically
hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)], is_closed=True, flags=1)

doc.saveas(OUTDIR / 'solid_hatch_islands_01.dxf')

# The second path has to set flag: 16 = outermost
hatch.paths.add_polyline_path([(1, 1), (9, 1), (9, 9), (1, 9)], is_closed=True, flags=16)

doc.saveas(OUTDIR / 'solid_hatch_islands_02.dxf')

# The third path has to set flag: 0 = default
hatch.paths.add_polyline_path([(2, 2), (8, 2), (8, 8), (2, 8)], is_closed=True, flags=0)

doc.saveas(OUTDIR / 'solid_hatch_islands_03.dxf')

# The forth path has to set flag: 0 = default, and so on
hatch.paths.add_polyline_path([(3, 3), (7, 3), (7, 7), (3, 7)], is_closed=True, flags=0)

doc.saveas(OUTDIR / 'solid_hatch_islands_04.dxf')
