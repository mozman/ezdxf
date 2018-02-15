import ezdxf
from ezdxf.addons import MengerSponge


def write(filename, sponge):
    dwg = ezdxf.new('R2000')
    sponge.render(dwg.modelspace())
    dwg.saveas(filename)


def main(filename, level=3, kind=0):
    print('building menger sponge <{}>: start'.format(kind))
    sponge = MengerSponge(level=level, kind=kind)
    print('building menger sponge <{}>: done'.format(kind))
    try:
        write(filename, sponge)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving menger sponge as "{}": done'.format(filename))


if __name__ == '__main__':
    main("dxf_original_menger_sponge.dxf", level=3, kind=0)
    main("dxf_menger_sponge_v1.dxf", level=3, kind=1)
    main("dxf_menger_sponge_v2.dxf", level=3, kind=2)
    main("dxf_jerusalem_cube.dxf", level=2, kind=3)
