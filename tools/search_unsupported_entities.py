# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.tools.test import find_unsupported_entities
from pathlib import Path

BASE_DXF_FOLDER = r'D:\source\dxftest'


def get_unsupported_entities(filename):
    unsupported_entities = set()
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=True)
    except IOError:
        return unsupported_entities
    except ezdxf.DXFError as e:
        print('\n' + '*' * 40)
        print('FOUND DXF ERROR: {}'.format(str(e)))
        print('*' * 40 + '\n')
        return unsupported_entities

    if dwg.dxfversion > 'AC1009':
        unsupported_entities.update(find_unsupported_entities(dwg.modelspace()))
        unsupported_entities.update(find_unsupported_entities(dwg.objects))
    return unsupported_entities


def process_dir(folder):
    for filename in folder.iterdir():
        if filename.is_dir():
            process_dir(filename)
        elif filename.match('*.dxf'):
            print("processing: {}".format(filename))
            unsupported_entities = get_unsupported_entities(filename)
            if len(unsupported_entities):
                print('\n' + '*'*40)
                for entity in unsupported_entities:
                    print('FOUND: {}'.format(entity))
                print('*' * 40 + '\n')


process_dir(Path(BASE_DXF_FOLDER))

