# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf import recover
from pathlib import Path


def _find_unused_blocks(doc):
    references = doc.query('INSERT')
    # block names are case insensitive!
    used_block_names = set(entity.dxf.name.lower() for entity in references)
    # exclude layout blocks, they are not referenced by any DXF entity
    existing_blocks = set(block.name.lower() for block in doc.blocks
                          if not block.is_layout_block)
    not_referenced_blocks = existing_blocks - used_block_names
    references_without_definition = used_block_names - existing_blocks

    if len(not_referenced_blocks):
        print('\nFound unused BLOCK definitions:\n')
        print('\n'.join(sorted(not_referenced_blocks)))

    if len(references_without_definition):
        print('\nFound BLOCK references without definition:\n')
        print('\n'.join(sorted(references_without_definition)))


def find_unused_blocks(filename):
    try:
        doc = ezdxf.readfile(filename)
    except IOError:
        return
    except ezdxf.DXFStructureError:
        try:
            print('Using recover mode.')
            doc, auditor = recover.readfile(filename)
        except ezdxf.DXFStructureError:
            print(f'DXF structure error!')
            return
    _find_unused_blocks(doc)


def process_dir(folder: Path):
    for filename in folder.iterdir():
        if filename.is_dir() and filename.stem != 'BigFiles':
            process_dir(filename)
        elif filename.match('*.dxf'):
            print(f"processing: {filename}")
            find_unused_blocks(filename)


process_dir(Path(ezdxf.EZDXF_TEST_FILES))

