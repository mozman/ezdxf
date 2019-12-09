import ezdxf
from ezdxf.addons import Importer


def merge(source, target):
    importer = Importer(source, target)
    # import all entities from source modelspace into target modelspace
    importer.import_modelspace()
    # import all required resources and dependencies
    importer.finalize()


base_dxf = ezdxf.readfile('file1.dxf')

for filename in ('file2.dxf', 'file3.dxf'):
    merge_dxf = ezdxf.readfile(filename)
    merge(merge_dxf, base_dxf)

# base_dxf.save()  # to save as file1.dxf
base_dxf.saveas('merged.dxf')
