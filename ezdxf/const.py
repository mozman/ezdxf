#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: constant values
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

acadrelease = {
    'AC1009': 'R12',
    'AC1012': 'R13',
    'AC1014': 'R14',
    'AC1015': 'R2000',
    'AC1018': 'R2004',
    'AC1021': 'R2007',
    'AC1024': 'R2010',
}

dxfversion = {
    acad: dxf for dxf, acad in acadrelease.items()
}
