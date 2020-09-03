# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf import recover
from pathlib import Path

DXF_ENTITY = 'SUNSTUDY'


def has_dxf_entity(filename, entity_name):
    try:
        doc = ezdxf.readfile(filename)
    except IOError:
        return False
    except ezdxf.DXFStructureError:
        try:
            print('Using recover mode.')
            doc, auditor = recover.readfile(filename)
        except ezdxf.DXFStructureError:
            print(f'DXF structure error!')
            return False

    entities = doc.modelspace().query(entity_name)
    if len(entities):
        return True
    entities = doc.objects.query(entity_name)
    return bool(len(entities))


def process_dir(folder: Path):
    for filename in folder.iterdir():
        if filename.is_dir() and filename.stem != 'BigFiles':
            process_dir(filename)
        elif filename.match('*.dxf'):
            print(f"processing: {filename}")
            if has_dxf_entity(filename, DXF_ENTITY):
                print('\n' + '*'*40)
                print(f'FOUND: {DXF_ENTITY}')
                print('*' * 40 + '\n')


process_dir(Path(ezdxf.EZDXF_TEST_FILES))

