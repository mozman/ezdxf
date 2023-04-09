#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable

PCL5_MODE = b"%0A;"
HPGL2_MODE = b"%0B;"
SEMICOLON = ord(";")

PRELUDE = b"%0B;IN;"
EPILOG = b"PU;PA0,0;"


def build(commands: Iterable[bytes]) -> bytes:
    output = bytearray(PRELUDE)
    for cmd in commands:
        output.extend(cmd)
        if output[-1] != SEMICOLON:
            output.append(SEMICOLON)
    output.extend(EPILOG)
    return bytes(output)
