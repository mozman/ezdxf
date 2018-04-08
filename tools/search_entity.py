# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from pathlib import Path

BASE_DXF_FOLDER = r'D:\source\dxftest'
DXF_ENTITY = 'TOLERANCE'


def has_dxf_entity(filename, entity_name):
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=True)
    except IOError:
        return False
    except ezdxf.DXFError as e:
        print('\n' + '*' * 40)
        print('FOUND DXF ERROR: {}'.format(str(e)))
        print('*' * 40 + '\n')
        return False
    else:
        entities = dwg.modelspace().query(entity_name)
        if len(entities):
            return True
        if 'objects' in dwg.sections:
            entities = dwg.objects.query(entity_name)
        return bool(len(entities))


def process_dir(folder):
    for filename in folder.iterdir():
        if filename.is_dir():
            process_dir(filename)
        elif filename.match('*.dxf'):
            print("processing: {}".format(filename))
            if has_dxf_entity(filename, DXF_ENTITY):
                print('\n' + '*'*40)
                print('FOUND: {}'.format(DXF_ENTITY))
                print('*' * 40 + '\n')


process_dir(Path(BASE_DXF_FOLDER))

