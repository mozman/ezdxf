import sys
from typing import cast
from pathlib import Path
import ezdxf
from ezdxf.entities import Insert

DIR = Path('~/Desktop/Inbox/ezdxf').expanduser()


def main():
    doc = ezdxf.readfile(DIR / 'crash_test_1.dxf')
    print(ezdxf.version)
    model_space = doc.modelspace()
    for entity in model_space:
        print(entity.dxftype())
        if entity.dxftype() == 'INSERT':
            entity = cast(Insert, entity)
            d = entity.dxf
            block_name = d.name
            print(f'Insert entity at {entity.dxf.insert} with scaling {entity.has_scaling} ({entity.has_uniform_scaling})')
            print(f'scaling = {d.xscale}, {d.yscale}, {d.zscale}')
            print(f'block = {block_name}')

            print('\nentities from block:')
            block = doc.blocks[block_name]
            for child in block:
                print(f'child: {child.dxftype()}')
                for key, value in child.dxf.all_existing_dxf_attribs().items():
                    print(f' - {key}: {value}')

            print('\nvirtual entities:')
            entities = entity.virtual_entities(non_uniform_scaling=True)
            for child in entities:
                print(f'child: {child.dxftype()}')


if __name__ == '__main__':
    main()