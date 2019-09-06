# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import os
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new

EXPORT_DIR = r'C:\Users\manfred\Desktop\outbox'


def create_doc(dxfversion):
    doc = ezdxf.new(dxfversion, setup=True)
    modelspace = doc.modelspace()
    modelspace.add_circle(center=(0, 0), radius=1.5, dxfattribs={
        'layer': 'test',
        'linetype': 'DASHED',
    })

    filename = os.path.join(EXPORT_DIR, '{}.dxf'.format(doc.acad_release))
    doc.saveas(filename)
    print("drawing '%s' created.\n" % filename)


if __name__ == '__main__':
    for version in versions_supported_by_new:
        create_doc(version)
