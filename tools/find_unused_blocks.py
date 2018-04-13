# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from pathlib import Path

BASE_DXF_FOLDER = r'D:\source\dxftest'
LAYOUT_NAMES = ('*PAPER_SPACE', '$PAPER_SPACE', '*MODEL_SPACE', '$MODEL_SPACE')


def _get_all_block_references(dwg):
    block_references = []
    for layout in dwg.layouts:
        block_references.extend(layout.query('INSERT'))
    for block in dwg.blocks:
        block_references.extend(block.query('INSERT'))
    return block_references


def _find_unused_blocks(dwg):
    def is_layout(block):
        name = block.name.upper()
        return any(name.startswith(layout_name) for layout_name in LAYOUT_NAMES)

    references = _get_all_block_references(dwg)
    used_block_names = set(entity.dxf.name for entity in references)
    existing_blocks = set(block.name for block in dwg.blocks if not is_layout(block))
    unused_blocks = existing_blocks - used_block_names
    references_without_definition = used_block_names - existing_blocks

    if len(unused_blocks):
        print('\nFound unused BLOCK definitions:\n')
        print('\n'.join(sorted(unused_blocks)))

    if len(references_without_definition):
        print('\nFound BLOCK references without definition:\n')
        print('\n'.join(sorted(references_without_definition)))


def find_unused_blocks(filename):
    try:
        dwg = ezdxf.readfile(filename, legacy_mode=True)
    except IOError:
        pass
    except ezdxf.DXFError as e:
        print('\n' + '*' * 40)
        print('FOUND DXF ERROR: {}'.format(str(e)))
        print('*' * 40 + '\n')
    else:
        _find_unused_blocks(dwg)


def process_dir(folder):
    for filename in folder.iterdir():
        if filename.is_dir():
            process_dir(filename)
        elif filename.match('*.dxf'):
            print("processing: {}".format(filename))
            find_unused_blocks(filename)


process_dir(Path(BASE_DXF_FOLDER))

