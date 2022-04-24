#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List
DATA = "prism.sat"


def parse_record(record: str) -> List[str]:
    return record.split(" ")


def merge_records(records):
    buffer = []
    for record in records:
        buffer.extend(record)
        if buffer[-1] == "#":
            yield list(buffer[:-1])
            buffer.clear()


"""
===============================================================================
Notes:

... I I I I are two infinite intervals (surface)

reversed/forward/forward_v ... Parameter defining the sense direction.


... @7 unknown
@=text 7=chars: "unknown"

The content is version dependent!

===============================================================================

0= body ~0 id() ~1 <lump-1> ~2 ~3
>>> ~0 ENTITY attribute 0-ptr 
>>> ~1 another attribute 0-ptr ???
>>> next-ptr <lump-1> BODY data ptr
>>> ~2 BODY wire 0-ptr
>>> ~3 BODY transform 0-ptr

1= lump ~ id() ~ ~ <shell-2> <body-0>
>>> next-ptr=<shell-2>, parent-ptr=<body-0>

2= shell ~ id() ~ ~ ~ <face-3> ~ <lump-1>
>>> next-ptr=<face-3>, parent-ptr=<lump-1>

3= face ~ id() ~ <face-4> <loop-5> <shell-2> ~ <plane-surface-6> forward single
>>> next-ptr=<face-4>, parent-ptr=<shell-2>
>>> <loop-5>
>>> <plane-surface-6>

5= loop ~ id() ~ ~ <coedge-10> <face-3>
>>> next-ptr=<coedge-10>, parent-ptr <face-3>

10= coedge ~ id() ~ <coedge-15> <coedge-16> <coedge-17> <edge-18> reversed <loop-5> ~
>>> 3x coedge, 1x edge-18, parent-ptr=<loop-5>

18= edge ~ id() ~ <vertex-32> <v0> <vertex-33> <v1> <coedge-17> <straight-curve-34> forward @7 unknown
>>> vertex-32 -> vertex-33, <coedge-17>?, <straight-curve-34>

32= vertex ~ id() ~ <edge-26> <point-55>
>>> <edge-26>?, <point-55>

55= point ~ id() ~ <v0> <v1> <v2>
>>> coordinates

34= straight-curve ~ id() ~ <v0> <v1> <v2> <v3> <v4> <v5> I I
>>> Unbounded ray (v0, v1, v2) -> (v3, v4, v5)

6= plane-surface ~ id() ~ <v0> <v1> <v2> <v3> <v4> <v5> <v6> <v7> <v8> forward_v I I I I
>>> unbounded plane by 3 points (v0, v1, v2) -> (v3, v4, v5) -> (v6, v7, v8)

   
"""


def is_float(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


class ACIS:
    def __init__(self):
        self.records: List[str] = []

    def parse_sat(self, data: str) -> None:
        lines = data.splitlines()
        records = [parse_record(l) for l in lines[3:]]
        self.records = list(merge_records(records))

    @staticmethod
    def load_sat(filename):
        with open(filename, "rt", encoding="cp1252") as fp:
            text = fp.read()
        acis = ACIS()
        acis.parse_sat(text)
        return acis

    def print_annotated_records(self, source=False):
        def resolve_pointer(ptr: str):
            rec_num = int(ptr[1:])
            if rec_num < 0:
                return "~"
            return f"<{self.records[rec_num][0]}-{rec_num}>"

        def annotate(tokens):
            yield tokens[0]  # name
            yield resolve_pointer(tokens[1])  # pointer to what
            yield "ID"
            value_count = 0
            for token in tokens[3:]:
                if token.startswith("$"):
                    yield resolve_pointer(token)
                elif is_float(token):
                    yield f"[{value_count}]"
                    value_count += 1
                else:
                    yield token

        for num, record in enumerate(self.records):
            if source:
                data = " ".join(record)
                print(f" src= {data} #")

            record = annotate(record)
            data = " ".join(record)
            print(f"{num:4d}= {data}")


def main():
    print("Legend:")
    print("--------------------------------------------------")
    print("0=         ... record number")
    print("~          ... null-pointer")
    print("ID         ... id-field")
    print("<entity-0> ... pointer to entity - record number")
    print("[0]        ... numbered data fields")
    print("--------------------------------------------------")
    acis = ACIS.load_sat(DATA)
    acis.print_annotated_records()


if __name__ == "__main__":
    main()
