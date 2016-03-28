#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: open DXF files with non standard encodings and from zip archives
# Created: 02.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

import ezdxf
import os

FILE_1 = r"D:\Source\dxftest\ChineseChars_cp936_R2004.dxf"
FILE_3 = r"D:\Source\dxftest\ChineseChars_cp936_R2004.zip"
FILE_4 = r"D:\Source\dxftest\ProE_AC1018.dxf"


def run_if_file_exists(func):
    def wrapper(filepath):
        if os.path.exists(filepath):
            func(filepath)
        else:
            print("skipped {}: file '{}' does not exist.".format(func.__name__, filepath))
    return wrapper


@run_if_file_exists
def read_plain_file(filename):
    print("Open DXF file: '{}'".format(filename))
    dwg = ezdxf.readfile(filename)
    print_stats(dwg)


@run_if_file_exists
def read_from_zip(filename):
    print("Open DXF file from ZIP archive: '{}'".format(filename))
    dwg = ezdxf.readzip(filename)
    print_stats(dwg)


def print_stats(dwg):
    print("Filename: {}".format(dwg.filename))
    print("Version: {}".format(dwg.dxfversion))
    print("encoding: {}".format(dwg.encoding))

# chinese chars 'cp936'
read_plain_file(FILE_1)
# chinese chars 'cp936' from zip file
read_from_zip(FILE_3)
# crappy ProE file
read_plain_file(FILE_4)