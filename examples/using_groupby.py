# Purpose: example for using the groupby feature
# Created: 03.02.2017
# Copyright (c) 2017 Manfred Moitzi
# License: MIT License
import os
import glob
import math
import ezdxf


def outname(fname):
    name, ext = os.path.splitext(fname)
    return name + '.txt'


def length(lines):
    def dist(s, e):
        dx = s[0] - e[0]
        dy = s[1] - e[1]
        return math.sqrt(dx * dx + dy * dy)

    return round(sum(dist(line.dxf.start, line.dxf.end) for line in lines))


# real world application:
# used by myself to collect masses for an effort estimation.
def calc(dxffile):
    def group_key(entity):  # group entities by (dxftype, layer)
        return entity.dxftype(), entity.dxf.layer

    dwg = ezdxf.readfile(dxffile)
    msp = dwg.modelspace()
    groups = msp.groupby(key=group_key)
    # using get(): returns None if key does not exist
    columns = groups.get(('CIRCLE', 'AR_ME_ST'))  # all CIRCLE entities on layer 'AR_ME_ST'
    outer_walls = groups.get(('LINE', 'AR_ME_AW'))  # all LINE entities on layer 'AR_ME_AW'
    inner_walls = groups.get(('LINE', 'AR_ME_IW'))  # all LINE entities on layer 'AR_ME_IW'
    beams = groups.get(('LINE', 'AR_ME_TR'))  # all LINE entities on layer 'AR_ME_TR'

    with open(outname(dxffile), 'wt', encoding='utf-8') as f:
        f.write("File: {}\n".format(dxffile))
        if columns is not None:
            f.write("Stützen Anzahl={}\n".format(len(columns)))
        if outer_walls is not None:
            f.write("Aussenwände Anzahl={}\n".format(len(outer_walls)))
            f.write("Aussenwände Gesamtlänge={}\n".format(length(outer_walls)))
        if inner_walls is not None:
            f.write("Innenwände Anzahl={}\n".format(len(inner_walls)))
            f.write("Innenwände Gesamtlänge={}\n".format(length(inner_walls)))
        if beams is not None:
            f.write("Träger Anzahl={}\n".format(len(beams)))
            f.write("Träger Gesamtlänge={}\n".format(length(beams)))


if __name__ == '__main__':
    for fname in glob.glob('*.dxf'):
        calc(fname)
