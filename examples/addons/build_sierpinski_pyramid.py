import ezdxf
from ezdxf.addons import SierpinskyPyramid


def write(filename, pyramids):
    dwg = ezdxf.new('R2000')
    pyramids.render(dwg.modelspace())
    dwg.saveas(filename)


def write_dxf_joined_pyramids(filename, pyramids):
    mesh = OptimizedMesh()
    faces = pyramids.faces()  # all pyramid faces have the same vertex order
    for vertices in pyramids:
        mesh.add_mesh(vertices, faces)
    with dxfmeshwriter(filename) as f:
        f.mesh(vertices=mesh.get_vertices(), faces=mesh.get_faces())


def main(filename, level, sides=3):
    print('building sierpinski pyramid {}: start'.format(sides))
    pyramids = SierpinskyPyramid(level=level, sides=sides)
    print('building sierpinski pyramid {}: done'.format(sides))
    try:
        write(filename, pyramids)
    except IOError as e:
        print('ERROR: can not write "{0}": {1}'.format(e.filename, e.strerror))
    else:
        print('saving "{}": done'.format(filename))


if __name__ == '__main__':
    main("dxf_sierpinski_pyramid_3.dxf", level=4, sides=3)
    main("dxf_sierpinski_pyramid_4.dxf", level=4, sides=4)
