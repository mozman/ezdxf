import ezdxf
from ezdxf.addons import SierpinskyPyramid


def write(filename, pyramids, merge=False):
    dwg = ezdxf.new('R2000')
    pyramids.render(dwg.modelspace(), merge=merge)
    dwg.saveas(filename)


def main(filename, level, sides=3, merge=False):
    print('building sierpinski pyramid {}: start'.format(sides))
    pyramids = SierpinskyPyramid(level=level, sides=sides)
    print('building sierpinski pyramid {}: done'.format(sides))
    try:
        write(filename, pyramids, merge=merge)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving "{}": done'.format(filename))


if __name__ == '__main__':
    main("dxf_sierpinski_pyramid_3.dxf", level=4, sides=3)
    main("dxf_sierpinski_pyramid_4.dxf", level=4, sides=4, merge=True)
