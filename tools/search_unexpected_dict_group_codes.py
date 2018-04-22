# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from pathlib import Path

BASE_DXF_FOLDER = r'D:\source\dxftest'


def get_dict_group_codes(filename):
    codes = set()
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=True)
    except IOError:
        return codes
    except ezdxf.DXFError as e:
        print('\n' + '*' * 40)
        print('FOUND DXF ERROR: {}'.format(str(e)))
        print('*' * 40 + '\n')
        return codes

    if dwg.dxfversion > 'AC1009':

        for d in dwg.objects.query('DICTIONARY ACDBDICTIONARYWDFLT'):
            for tag in d.tags.get_subclass('AcDbDictionary'):
                codes.add(tag.code)

    return codes


def process_dir(folder):
    for filename in folder.iterdir():
        if filename.is_dir():
            process_dir(filename)
        elif filename.match('*.dxf'):
            print("processing: {}".format(filename))
            codes = get_dict_group_codes(filename)
            unexpected_codes = codes - {-101, 100, 280, 281}
            if len(unexpected_codes):
                print('\n' + '*'*40)
                print('FOUND UNEXPECTED GROUP CODES: {}'.format(str(unexpected_codes)))
                print('*' * 40 + '\n')


process_dir(Path(BASE_DXF_FOLDER))

