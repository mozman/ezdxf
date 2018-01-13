# Purpose: compiler for line type defintions
# Created: 12.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License

# Auszug acadlt.lin
#
# *RAND,Rand __ __ . __ __ . __ __ . __ __ . __ __ .
# A,.5,-.25,.5,-.25,0,-.25
# *RAND2,Rand (.5x) __.__.__.__.__.__.__.__.__.__.__.
# A,.25,-.125,.25,-.125,0,-.125
# *RANDX2,Rand (2x) ____  ____  .  ____  ____  .  ___
# A,1.0,-.5,1.0,-.5,0,-.5
#
# *MITTE,Mitte ____ _ ____ _ ____ _ ____ _ ____ _ ____
# A,1.25,-.25,.25,-.25
# *CENTER2,Mitte (.5x) ___ _ ___ _ ___ _ ___ _ ___ _ ___
# A,.75,-.125,.125,-.125
# *MITTEX2,Mitte (2x) ________  __  ________  __  _____
# A,2.5,-.5,.5,-.5
#
# ;;  Komplexe Linientypen
# ;;
# ;;  Dieser Datei sind komplexe Linientypen hinzugefügt worden.
# ;;  Diese Linientypen wurden in LTYPESHP.LIN in
# ;;  Release 13 definiert und wurden in ACAD.LIN in
# ;;  Release 14 aufgenommen.
# ;;
# ;;  Diese Linientypdefinitionen verwenden LTYPESHP.SHX.
# ;;
# *GRENZE1,Grenze rund ----0-----0----0-----0----0-----0--
# A,.25,-.1,[CIRC1,ltypeshp.shx,x=-.1,s=.1],-.1,1
# *GRENZE2,Grenze eckig ----[]-----[]----[]-----[]----[]---
# A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
# *EISENBAHN,Eisenbahn -|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-
# A,.15,[TRACK1,ltypeshp.shx,s=.25],.15
# *ISOLATION,Isolation SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
# A,.0001,-.1,[BAT,ltypeshp.shx,x=-.1,s=.1],-.2,[BAT,ltypeshp.shx,r=180,x=.1,s=.1],-.1
# *HEISSWASSERLEITUNG,Heißwasserleitung ---- HW ---- HW ---- HW ----
# A,.5,-.2,["HW",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.2
# *GASLEITUNG,Gasleitung ----GAS----GAS----GAS----GAS----GAS----GAS--
# A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25
# *ZICKZACK,Zickzack /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# A,.0001,-.2,[ZIG,ltypeshp.shx,x=-.2,s=.2],-.4,[ZIG,ltypeshp.shx,r=180,x=.2,s=.2],-.2

from ..lldxf.const import DXFValueError
from ..lldxf.tags import DXFTag


def lin_compiler(definition):
    """
    Compiles line type definitions like 'A,.5,-.25,.5,-.25,0,-.25' or 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    into DXFTags().

    Args:
        definition: definition string

    Returns:
        list of DXFTag()
    """
    def tokenizer():
        bag = []
        for part in lin_parser(definition):
            try:
                value = float(part)
                bag.append(value)
                continue
            except ValueError:
                pass

            if part.startswith('["'):
                bag.append('[TEXT')
                bag.append(part[2:-1])  # text ohne '["' und '"'
            elif part.startswith('['):
                bag.append('[SHAPE')
                bag.append(part[1:])  # text ohne '['
            else:
                _part = part.rstrip(']')
                subparts = _part.split('=')
                if len(subparts) == 2:
                    bag.append(subparts[0].lower())
                    bag.append(float(subparts[1]))
                else:
                    bag.append(_part)
            if part.endswith(']'):
                bag.append(']')

    # 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    # ['A', .5, -.2, '[TEXT', 'GAS', 'STANDARD', 's', .1, 'u', 0.0, 'x', -.1, 'y', -.05, ']', -.25]
    tokens = list(reversed(tokenizer()))
    while tokens:
        tag = tokens.pop()
        if isinstance(tag, float):
            yield DXFTag(999, tag)
        elif tag == 'A':
            continue
        elif tag == '[TEXT':
            while tag != ']':
                tag = tokens.pop()
        elif tag == '[SHAPE':
            while tag != ']':
                tag = tokens.pop()


def lin_parser(definition):
    part = ''
    escape = False
    for char in definition:
        if char == ',' and not escape:
            yield part
            part = ''
            continue
        part += char
        if char == '"':
            escape = not escape
    if escape:
        raise DXFValueError("Line type parsing error: '{}'".format(definition))
    if part:
        yield part
