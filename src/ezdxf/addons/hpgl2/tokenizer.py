#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple, Sequence


class Command(NamedTuple):
    name: str
    args: Sequence[bytes]


ESCAPE = 27
SEMICOLON = ord(";")
PERCENT = ord("%")
MINUS = ord("-")
QUOTE_CHAR = ord('"')
CHAR_A = ord("A")
CHAR_B = ord("B")
CHAR_Z = ord("Z")
CHAR_P = ord("P")
CHAR_E = ord("E")

# Enter HPGL/2 mode commands
# b"%-0B",  # ??? not documented (assumption)
# b"%-1B",  # ??? not documented (really exist)
# b"%-2B",  # ??? not documented (assumption)
# b"%-3B",  # ??? not documented (assumption)
# b"%0B",  # documented in the HPGL2 reference by HP
# b"%1B",  # documented
# b"%2B",  # documented
# b"%3B",  # documented

def get_enter_hpgl2_mode_command_length(s: bytes, i: int) -> int:
    try:
        if s[i] != ESCAPE:
            return 0
        if s[i + 1] != PERCENT:
            return 0
        length = 4
        if s[i + 2] == MINUS:
            i += 1
            length = 5
        # 0, 1, 2 or 3 + "B"
        if 47 < s[i + 2] < 52 and s[i + 3] == CHAR_B:
            return length
    except IndexError:
        pass
    return 0

def skip_to_hpgl2(s: bytes, start: int) -> int:
    while True:
        try:
            index = s.index(b"%", start)
        except ValueError:
            return len(s)
        length = get_enter_hpgl2_mode_command_length(s, index)
        if length:
            return index + length
        start += 2


def hpgl2_commands(s: bytes) -> list[Command]:
    def is_letter(c):
        return CHAR_A <= c <= CHAR_Z

    def find_closing_quote_char(i: int):
        while i < length and s[i] != QUOTE_CHAR:
            i += 1
        return i

    def find_terminator(i: int):
        while i < length:
            c = s[i]
            if c == QUOTE_CHAR:
                i = find_closing_quote_char(i + 1)
            elif is_letter(c) or c == SEMICOLON or c == ESCAPE:
                break
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

    length = len(s)
    index = skip_to_hpgl2(s, 0)
    while index < length:
        char = s[index]

        start = index
        if char == ESCAPE:
            index = skip_to_hpgl2(s, index)
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
