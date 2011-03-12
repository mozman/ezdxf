#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R2000/AC1015
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from functools import partial
from .hdrvars import SingleValue, Point2D, Point3D

from .ac1009 import AC1009Engine

class AC1015Engine(AC1009Engine):
    def __init__(self):
        super(AC1015Engine, self).__init__()
        self.HEADERVARS.update(AC1015VARMAP)

AC1015VARMAP = {
    '$ACADMAINTVER': partial(SingleValue, code=70),
    '$CELTSCALE': partial(SingleValue, code=40),
    '$CEWEIGHT': partial(SingleValue, code=370),
    '$CPSNID': partial(SingleValue, code=390),
    '$CEPSNTYPE': partial(SingleValue, code=380),
    '$CHAMFERC': partial(SingleValue, code=40),
    '$CHAMFERD': partial(SingleValue, code=40),
    '$CMLSCALE': partial(SingleValue, code=40),
    '$CMSTYLE': partial(SingleValue, code=2),
    '$DIMALTRND': partial(SingleValue, code=40),
    '$DIMALTTD': partial(SingleValue, code=70),
    '$DIMALTTZ': partial(SingleValue, code=70),
    '$DIMALTU': partial(SingleValue, code=70),
    '$DIMALTZ': partial(SingleValue, code=70),
    '$DIMATFIT': partial(SingleValue, code=70),
    '$DIMAUNIT': partial(SingleValue, code=70),
    '$DIMAZIN': partial(SingleValue, code=70),
    '$DIMDEC': partial(SingleValue, code=70),
    '$DIMDSEP': partial(SingleValue, code=70),
    '$DIMEXE': partial(SingleValue, code=40),
    '$DIMEXO': partial(SingleValue, code=40),
    '$DIMGAP': partial(SingleValue, code=40),
    '$DIMLFAC': partial(SingleValue, code=40),
    '$DIMLUNIT': partial(SingleValue, code=70),
    '$DIMLWD': partial(SingleValue, code=70),
    '$DIMLWE': partial(SingleValue, code=70),
    '$DIMSD1': partial(SingleValue, code=70),
    '$DIMSD2': partial(SingleValue, code=70),
    '$DIMTDEC': partial(SingleValue, code=70),
    '$DIMTMOVE': partial(SingleValue, code=70),
    '$DIMTOFL': partial(SingleValue, code=70),
    '$DIMTXSTY': partial(SingleValue, code=7),
    '$DIMUPT': partial(SingleValue, code=70),
    '$DISPSIHL': partial(SingleValue, code=70),
    '$ENDCAPS': partial(SingleValue, code=280),
    '$EXTNAMES': partial(SingleValue, code=290),
    '$FINGERPRINTGUI': partial(SingleValue, code=2),
    '$HYPERLINKBASE': partial(SingleValue, code=1),
    '$INSBASE': Point3D,
    '$MEASUREMENT': partial(SingleValue, code=70),
    '$MENU': partial(SingleValue, code=1),
    '$PINSBASE': Point3D,
    '$PROXYGRAPHICS': partial(SingleValue, code=70),
    '$PSTYLEMODE': partial(SingleValue, code=290),
    '$PSVPSCALE': partial(SingleValue, code=40),
    '$PUCSORGBACK': Point3D,
    '$PUCSORGBOTTOM': Point3D,
    '$PUCSORGFRONT': Point3D,
    '$PUCSORGLEFT': Point3D,
    '$PUCSORGRIGHT': Point3D,
    '$PUCSORGTOP': Point3D,
    '$PUCSORTHOREF': partial(SingleValue, code=2),
    '$PUCSORTHOVIEW': partial(SingleValue, code=70),
    '$TDUCREATE': partial(SingleValue, code=40),
    '$TREEDEPTH': partial(SingleValue, code=70),
    '$UCSBASE': partial(SingleValue, code=2),
    '$UCSORGBACK': Point3D,
    '$UCSORGBOTTOM': Point3D,
    '$UCSORGFRONT': Point3D,
    '$UCSORGLEFT': Point3D,
    '$UCSORGRIGHT': Point3D,
    '$UCSORGTOP': Point3D,
    '$UCSORTHOREF': partial(SingleValue, code=2),
    '$UCSORTHOVIEW': partial(SingleValue, code=70),
    '$VERSIONGUID': partial(SingleValue, code=2),
    '$XEDIT': partial(SingleValue, code=290),
}