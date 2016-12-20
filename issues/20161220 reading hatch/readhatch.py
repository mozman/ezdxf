import ezdxf

# import svgwrite

filename = 'DEMO-BLock'

dwg_dxf = ezdxf.readfile(filename + '.dxf')
modelspace = dwg_dxf.modelspace()

for e in modelspace.query('HATCH'):
    with e.edit_boundary() as b:
        print(b.paths)
        for p in b.paths:
            print(p.path_type_flags)
            print(p.edges)
            print(p.source_boundary_objects)
