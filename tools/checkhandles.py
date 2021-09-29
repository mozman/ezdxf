# Author:  mozman <me@mozman.at>
# Purpose: check dxf handles
# Created: 14.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License

import sys

from ezdxf.lldxf.tags import ascii_tags_loader
from ezdxf.lldxf.validator import dxf_info

FORMAT = (
    "ACAD release: {0.release}\n"
    "DXF Version: {0.version}\n"
    "$HANDSEED: {0.handseed}"
)


def printhandles(handles, info):
    print(FORMAT.format(info))
    print("%d handles found." % len(handles))
    sortedhandles = sorted(handles)
    print("min handle: %X" % sortedhandles[0])
    print("max handle: %X" % sortedhandles[-1])
    printduplicates(sortedhandles)


def printduplicates(handles):
    count = 0
    for index in range(len(handles) - 1):
        h1 = handles[index]
        h2 = handles[index + 1]
        if h1 == h2:
            count += 1
    if count > 1:
        print("found %d duplicate handles" % count)


def checkhandles(stream):
    info = dxf_info(stream)
    stream.seek(0)
    handles = []
    lineno = 1
    iterator = ascii_tags_loader(stream, skip_comments=False)
    for tag in iterator:
        if tag.code in (5, 105):
            try:
                handle = int(tag.value, 16)
            except ValueError:
                print("invalid handle at line number %d" % lineno)
            else:
                handles.append(handle)
        lineno += 2
    printhandles(handles, info)


def main(dxffilename):
    with open(dxffilename) as fp:
        checkhandles(fp)


if __name__ == "__main__":
    main(sys.argv[1])
