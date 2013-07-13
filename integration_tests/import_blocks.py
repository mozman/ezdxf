#!/usr/bin/env python3
# encoding: utf-8
# Purpose: 
# Created: 13.07.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import ezdxf

def main():
    source_dwg = ezdxf.readfile('CustomBlocks.dxf')
    target_dwg = ezdxf.new(source_dwg.dxfversion)
    importer = ezdxf.Importer(source_dwg, target_dwg)
    importer.import_blocks(query='CustomBlock1')
    importer.import_modelspace_entities()
    target_dwg.saveas("CustomBlocks_Import.dxf")

if __name__ == '__main__':
    main()
