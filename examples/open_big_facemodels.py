#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: open example files with big polyface models
# Created: 23.04.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

__author__ = 'manfred'

import ezdxf


def count_meshes(entities):
    polyface_count = 0
    polymesh_count = 0
    for entity in entities:
        if entity.get_mode() == 'AcDbPolyFaceMesh':
            polyface_count += 1
        elif entity.get_mode() == 'AcDbPolygonMesh':
            polymesh_count += 1
    return polyface_count, polymesh_count


def print_stats(filename):
    print('opening DXF file: {}'.format(filename))
    dwg = ezdxf.readfile(filename)
    print("DXF version: {}".format(dwg.dxfversion))
    print("Database contains {} entities.".format(len(dwg.entitydb)))
    polylines = dwg.entities.query('POLYLINE')
    polyface_count, polymesh_count = count_meshes(polylines)
    print("PolyFaceMeshes: {}".format(polyface_count))
    print("PolygonMeshes {}".format(polymesh_count))

if __name__ == '__main__':
    #print_stats(r'D:\Source\ezdxf-dev\integration_tests\polyface_AC1015.dxf')
    #print_stats(r'D:\Source\ezdxf-dev\integration_tests\polymesh_AC1015.dxf')
    print_stats(r'D:\Source\dxftest\fanuc-430-arm.dxf')
    print_stats(r'D:\Source\dxftest\cnc machine.dxf')