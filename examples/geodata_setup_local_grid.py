#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf

OUTBOX = pathlib.Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new('R2010', units=6)
msp = doc.modelspace()
gdat = msp.new_geodata()
gdat.setup_local_grid(
    design_point=(0, 0),
    reference_point=(1718030, 5921664)
)
msp.add_line((0, 0), (100, 0))
doc.set_modelspace_vport(50, center=(50, 0))
doc.saveas(OUTBOX / 'geodata_local_grid.dxf')

