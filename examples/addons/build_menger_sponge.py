# Copyright (C) 2018 Manfred Moitzi
# License: MIT License
import math
import ezdxf
from ezdxf.addons import MengerSponge
from ezdxf.ezmath.matrix44 import Matrix44


def write(filename, sponge, merge=False):
    dwg = ezdxf.new('R2000')
    transform = Matrix44.chain(Matrix44.z_rotate(math.radians(45)), Matrix44.translate(5, 3, 4))
    sponge.render(dwg.modelspace(), merge=merge, matrix=transform)
    dwg.saveas(filename)


def main(filename, level=3, kind=0, merge=False):
    print('building menger sponge <{}>: start'.format(kind))
    sponge = MengerSponge(level=level, kind=kind)
    print('building menger sponge <{}>: done'.format(kind))
    try:
        write(filename, sponge, merge)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving menger sponge as "{}": done'.format(filename))


if __name__ == '__main__':
    main("dxf_original_menger_sponge.dxf", level=3, kind=0)
    main("dxf_menger_sponge_v1.dxf", level=3, kind=1)
    main("dxf_menger_sponge_v2.dxf", level=3, kind=2)
    main("dxf_jerusalem_cube.dxf", level=2, kind=3, merge=True)
