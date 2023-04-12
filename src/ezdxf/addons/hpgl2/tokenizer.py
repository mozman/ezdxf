#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple, Sequence


class Command(NamedTuple):
    name: str
    args: Sequence[bytes]


ESCAPE = 27
SEMICOLON = ord(";")
CHAR_A = ord("A")
CHAR_Z = ord("Z")
CHAR_P = ord("P")
CHAR_E = ord("E")


def hpgl2_commands(s: bytes) -> list[Command]:
    def is_letter(c):
        return CHAR_A <= c <= CHAR_Z

    def find_terminator(i: int):
        while i < length and not is_letter(s[i]) and s[i] != SEMICOLON:
            i += 1
        return i

    def append_command(b: bytes):
        commands.append(make_command(b))

    def make_command_until(mark: int) -> int:
        i = index
        while i < length and s[i] != mark:
            i += 1
        append_command(s[start:i])
        return i + 1

    commands: list[Command] = []
    index = 0
    length = len(s)
    while index < length:
        char = s[index]

        start = index
        if char == ESCAPE:
            index = make_command_until(SEMICOLON)
            continue

        if char <= 32:  # skip all white space and control chars
            index += 1
            continue

        if s[start] == CHAR_P and s[start + 1] == CHAR_E:
            index = make_command_until(SEMICOLON)
            continue

        index_plus_2 = index + 2
        if index_plus_2 >= length:
            append_command(s[index:])
            break

        third_char = s[index_plus_2]
        if third_char == SEMICOLON:
            append_command(s[index:index_plus_2])
            index += 3
            continue

        if is_letter(third_char):
            append_command(s[index:index_plus_2])
            index = index_plus_2
            continue

        index = find_terminator(index_plus_2)
        append_command(s[start:index])
        if index < length and s[index] == SEMICOLON:
            index += 1
    return commands


def make_command(cmd: bytes) -> Command:
    if not cmd:
        return Command("NOOP", tuple())
    if cmd[0] == ESCAPE:
        return Command("ESCAPE", (cmd,))
    name = cmd[:2]
    args = tuple(s for s in cmd[2:].split(b","))
    return Command(name.decode(), args)


def pe_encode(value: float, decimal_places: int = 0, base: int = 64) -> bytes:
    if decimal_places:
        n = round(decimal_places * 3.33)
        value *= 2 << n
        x = round(value)
    else:
        x = round(value)
    if x >= 0:
        x *= 2
    else:
        x = abs(x) * 2 + 1

    chars = bytearray()
    while x >= base:
        x, r = divmod(x, base)
        chars.append(63 + r)
    if base == 64:
        chars.append(191 + x)
    else:
        chars.append(95 + x)
    return bytes(chars)


def pe_decode(
    s: bytes, decimal_places: int = 0, base=64, start: int = 0
) -> tuple[list[float], int]:
    def _decode():
        factors.reverse()
        x = 0
        for f in factors:
            x = x * base + f
        factors.clear()
        if x & 1:
            x = -(x - 1)
        x = x >> 1
        return x

    if base == 64:
        terminator = 191
    else:
        terminator = 95
    values: list[float] = []
    factors = []
    for index in range(start, len(s)):
        value = s[index]
        if value < 63:
            return values, index
        if value >= terminator:
            factors.append(value - terminator)
            x = _decode()
            if decimal_places:
                n = 2 << round(decimal_places * 3.33)
                values.append(round(x / n, decimal_places))
            else:
                values.append(round(float(x), decimal_places))
        else:
            factors.append(value - 63)
    return values, len(s)
