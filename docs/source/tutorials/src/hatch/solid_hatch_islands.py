from pathlib import Path

OUTDIR = Path("~/Desktop/Outbox").expanduser()

import ezdxf

doc = ezdxf.new("R2000")
doc.set_modelspace_vport(15, center=(5, 5))
msp = doc.modelspace()

hatch = msp.add_hatch(
    color=1,
    dxfattribs={
        "hatch_style": ezdxf.const.HATCH_STYLE_NESTED,
        # 0 = nested: ezdxf.const.HATCH_STYLE_NESTED
        # 1 = outer: ezdxf.const.HATCH_STYLE_OUTERMOST
        # 2 = ignore: ezdxf.const.HATCH_STYLE_IGNORE
    },
)

# The first path has to set flag: 1 = external
# flag const.BOUNDARY_PATH_POLYLINE is added (OR) automatically
hatch.paths.add_polyline_path(
    [(0, 0), (10, 0), (10, 10), (0, 10)],
    is_closed=True,
    flags=ezdxf.const.BOUNDARY_PATH_EXTERNAL,
)

doc.saveas(OUTDIR / "solid_hatch_islands_01.dxf")

# The second path has to set flag: 16 = outermost
hatch.paths.add_polyline_path(
    [(1, 1), (9, 1), (9, 9), (1, 9)],
    is_closed=True,
    flags=ezdxf.const.BOUNDARY_PATH_OUTERMOST,
)

doc.saveas(OUTDIR / "solid_hatch_islands_02.dxf")

# The third path has to set flag: 0 = default
hatch.paths.add_polyline_path(
    [(2, 2), (8, 2), (8, 8), (2, 8)],
    is_closed=True,
    flags=ezdxf.const.BOUNDARY_PATH_DEFAULT,
)

doc.saveas(OUTDIR / "solid_hatch_islands_03.dxf")

# The forth path has to set flag: 0 = default, and so on
hatch.paths.add_polyline_path(
    [(3, 3), (7, 3), (7, 7), (3, 7)],
    is_closed=True,
    flags=ezdxf.const.BOUNDARY_PATH_DEFAULT,
)

doc.saveas(OUTDIR / "solid_hatch_islands_04.dxf")
