# Copyright (c) 2011, Manfred Moitzi
# License: MIT License
import ezdxf


def main():
    doc = ezdxf.new('AC1009')

    # block creation
    block = doc.blocks.new('TEST')
    block.add_line((-1, -1), (+1, +1))
    block.add_line((-1, +1), (+1, -1))

    # block usage
    ms = doc.modelspace()
    ms.add_blockref('TEST', (5, 5))
    doc.saveas('using_blocks.dxf')


if __name__ == '__main__':
    main()
