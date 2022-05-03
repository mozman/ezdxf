#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Iterator
from argparse import ArgumentParser

from ezdxf._acis.sat import merge_record_strings

"""
===============================================================================
Notes:

... I I I I are two infinite intervals (surface)

reversed/forward/forward_v ... Parameter defining the sense direction.


... @7 unknown
@=text 7=char count: "unknown"

SAT/SAB support ngons as polygon faces

The content is version dependent!

===============================================================================

0= body ~0 ID ~1 <lump-1> ~2 ~3
>>> ~0 ENTITY attribute 0-ptr 
>>> ~1 another attribute 0-ptr ???
>>> next-ptr <lump-1> BODY data ptr
>>> ~2 BODY wire 0-ptr
>>> ~3 BODY transform 0-ptr

1= lump ~ ID ~ ~ <shell-2> <body-0>
>>> next-ptr=<shell-2>, parent-ptr=<body-0>

2= shell ~ ID ~ ~ ~ <face-3> ~ <lump-1>
>>> next-ptr=<face-3>, parent-ptr=<lump-1>

3= face ~ ID ~ <face-4> <loop-5> <shell-2> ~ <plane-surface-6> forward single
>>> next-ptr=<face-4>, parent-ptr=<shell-2>
>>> <loop-5>
>>> <plane-surface-6>

5= loop ~ ID ~ ~ <coedge-10> <face-3>
>>> next-ptr=<coedge-10>, parent-ptr <face-3>
>>> loop-5 begins at coedge-10

10= coedge ~ ID ~ <coedge-15> <coedge-16> <coedge-17> <edge-18> reversed <loop-5> ~
>>> triangle: <coedge-10> -> <coedge-15> -> <coedge-16> => <coedge-10>
>>> <coedge-17> is the same edge in <loop-20>
>>> <edge-18> defines the vertices, same as in <coedge-17>
>>> reversed: edge orientation reversed cw/ccw?
>>> parent-ptr=<loop-5>

15= coedge ~ ID ~ <coedge-16> <coedge-10> <coedge-27> <edge-28> forward <loop-5> ~
16= coedge ~ ID ~ <coedge-10> <coedge-15> <coedge-29> <edge-30> reversed <loop-5> ~

17= coedge ~ ID ~ <coedge-31> <coedge-25> <coedge-10> <edge-18> forward <loop-20> ~
>>> <coedge-10> is the same edge in <loop-5>
>>> triangle: <coedge-17> -> <coedge-31> -> <coedge-25> => <coedge-17>
>>> <edge-18> defines the vertices, same as in <coedge-10>
>>> forward: edge orientation forward, must be contraire to <coedge-10> to have
    consistent face normals
>>> parent-ptr=<loop-20>

18= edge ~ ID ~ <vertex-32> [0] <vertex-33> [1] <coedge-17> <straight-curve-34> forward @7 unknown
>>> vertex-32 -> vertex-33
>>> is also used by <coedge-17> 
>>> <straight-curve-34> defines the kind of edge

32= vertex ~ ID ~ <edge-26> <point-55>
>>> <edge-26> also uses <vertex-32>
>>> <point-55> finally some coordinates

55= point ~ id() ~ [0] [1] [2]
>>> coordinates

34= straight-curve ~ ID ~ [0] [1] [2] [3] [4] [5] I I
>>> Unbounded ray: origin=([0], [1], [2]) direction=([3], [4], [5])
>>> bounded: origin + lower_bound * direction, origin + upper_bound * direction?

6= plane-surface ~ ID ~ [0] [1] [2] [3] [4] [5] [6] [7] [8] forward_v I I I I
>>> unbounded plane: origin=([0], [1], [2]), u-direction=([3], [4], [5]), v-direction=([6], [7], [8])
>>> normal-vector= u-direction <cross> v-direction?

"""


def parse_record(record: str) -> List[str]:
    return record.split(" ")


def is_float(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


class SatAnalyzer:
    def __init__(self):
        self.records: List[str] = []

    def parse_sat(self, data: str) -> None:
        lines = data.splitlines()
        records = merge_record_strings(lines[3:])
        self.records = list(parse_record(r) for r in records)

    @staticmethod
    def sat_loads(s: str):
        acis = SatAnalyzer()
        acis.parse_sat(s)
        return acis

    def annotated_records(
        self, filter_func=lambda r: True, source=False
    ) -> Iterator[str]:
        """Yields the annotate ACIS records.

        Example::

           0= body ~ ID ~ <lump-1> ~ ~
           1= lump ~ ID ~ ~ <shell-2> <body-0>
           2= shell ~ ID ~ ~ ~ <face-3> ~ <lump-1>
           3= face ~ ID ~ <face-4> <loop-5> <shell-2> ~ <plane-surface-6> forward single
           4= face ~ ID ~ <face-7> <loop-8> <shell-2> ~ <plane-surface-9> forward single
           5= loop ~ ID ~ ~ <coedge-10> <face-3>
           6= plane-surface ~ ID ~ [0] [1] [2] [3] [4] [5] [6] [7] [8] forward_v I I I I

        =========== =================================================
        0=          record number, always the 1st field
        ~           null-pointer
        ID          id-field, always the 3rd field
        <entity-0>  pointer to entity - record number
        [0]         numbered data fields
        =========== =================================================

        Args:
            filter_func: a function which returns True or False for a given
                record, which indicates if a record should be processed
            source: yield also the source record if true

        """

        def resolve_pointer(ptr: str):
            rec_num = int(ptr[1:])
            if rec_num < 0:
                return "~"
            return f"<{self.records[rec_num][0]}-{rec_num}>"

        def annotate(tokens):
            yield tokens[0]  # entity name
            yield resolve_pointer(tokens[1])  # attribute pointer
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
            if not filter_func(record):
                continue
            if source:
                data = " ".join(record)
                yield f" src= {data} #"
            record = annotate(record)
            data = " ".join(record)
            yield f"{num:4d}= {data}"


LEGEND = [
    "Legend:",
    "--------------------------------------------------",
    "0=         ... record number",
    "~          ... null-pointer",
    "ID         ... id-field",
    "<entity-0> ... pointer to entity - record number",
    "[0]        ... numbered data fields",
    "--------------------------------------------------",
]


def print_legend():
    for line in LEGEND:
        print(line)


def main():
    parser = ArgumentParser()
    parser.add_argument("file", nargs="?")
    parser.add_argument(
        "-s",
        "--source",
        action="store_true",
        default=False,
        help="print source content too",
    )
    args = parser.parse_args()
    if args.file:
        with open(args.file[0], "rt") as fp:
            sat = fp.read()
    else:
        sat = PRISM

    print_legend()
    acis = SatAnalyzer.sat_loads(sat)
    for s in acis.annotated_records(source=args.source):
        print(s)


PRISM = """700 0 1 0 
@33 Open Design Alliance ACIS Builder @12 ACIS 32.0 NT @24 Sat Apr 23 14:32:04 2022 
1 9.9999999999999995e-007 1e-010 
body $-1 -1 $-1 $1 $-1 $-1 #
lump $-1 -1 $-1 $-1 $2 $0 #
shell $-1 -1 $-1 $-1 $-1 $3 $-1 $1 #
face $-1 -1 $-1 $4 $5 $2 $-1 $6 forward single #
face $-1 -1 $-1 $7 $8 $2 $-1 $9 forward single #
loop $-1 -1 $-1 $-1 $10 $3 #
plane-surface $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 -0.21225108629643399 -0.6119059387325364 0.76191902359098318 -0.058576759801332381 -0.77031527097506436 -0.63496704364383372 forward_v I I I I #
face $-1 -1 $-1 $11 $12 $2 $-1 $13 forward single #
loop $-1 -1 $-1 $-1 $14 $4 #
plane-surface $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 -0.9152049609788877 0.19252196236278163 -0.3540270800484287 0.35569002591177251 -0.027047586873346612 -0.93421252052796389 forward_v I I I I #
coedge $-1 -1 $-1 $15 $16 $17 $18 reversed $5 $-1 #
face $-1 -1 $-1 $19 $20 $2 $-1 $21 forward single #
loop $-1 -1 $-1 $-1 $22 $7 #
plane-surface $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.9973445351432173 -0.058886394872714735 -0.042851729473322366 0.042734476776907795 -0.0032496398237411763 0.99908118005276214 forward_v I I I I #
coedge $-1 -1 $-1 $23 $24 $25 $26 forward $8 $-1 #
coedge $-1 -1 $-1 $16 $10 $27 $28 forward $5 $-1 #
coedge $-1 -1 $-1 $10 $15 $29 $30 reversed $5 $-1 #
coedge $-1 -1 $-1 $31 $25 $10 $18 forward $20 $-1 #
edge $-1 -1 $-1 $32 0 $33 3.7701727831654939 $17 $34 forward @7 unknown #
face $-1 -1 $-1 $35 $36 $2 $-1 $37 forward single #
loop $-1 -1 $-1 $-1 $31 $11 #
plane-surface $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 0.35424919523921139 -0.91480990045388144 0.19398544714470417 -0.016229036731927417 -0.21342038839667235 -0.97682565291016354 forward_v I I I I #
coedge $-1 -1 $-1 $29 $38 $39 $40 reversed $12 $-1 #
coedge $-1 -1 $-1 $24 $14 $41 $42 reversed $8 $-1 #
coedge $-1 -1 $-1 $14 $23 $43 $44 forward $8 $-1 #
coedge $-1 -1 $-1 $17 $31 $14 $26 reversed $20 $-1 #
edge $-1 -1 $-1 $32 0 $45 2.1386001334682128 $14 $46 forward @7 unknown #
coedge $-1 -1 $-1 $47 $48 $15 $28 reversed $49 $-1 #
edge $-1 -1 $-1 $32 0 $50 2.7374750783627975 $15 $51 forward @7 unknown #
coedge $-1 -1 $-1 $38 $22 $16 $30 forward $12 $-1 #
edge $-1 -1 $-1 $33 0 $50 3.140963148546323 $29 $52 forward @7 unknown #
coedge $-1 -1 $-1 $25 $17 $53 $54 reversed $20 $-1 #
vertex $-1 -1 $-1 $26 $55 #
vertex $-1 -1 $-1 $54 $56 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 0.74654296021490529 0.40157805240031325 0.53047966632467436 I I #
face $-1 -1 $-1 $57 $49 $2 $-1 $58 forward single #
loop $-1 -1 $-1 $-1 $59 $19 #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.90029791640739398 -0.20794591431152187 0.38239006058428165 -0.39665189696405329 0.030162433186344435 -0.91747343299906914 forward_v I I I I #
coedge $-1 -1 $-1 $22 $29 $60 $61 forward $12 $-1 #
coedge $-1 -1 $-1 $62 $53 $22 $40 forward $63 $-1 #
edge $-1 -1 $-1 $33 0 $64 2.6484597207512501 $39 $65 forward @7 unknown #
coedge $-1 -1 $-1 $53 $62 $23 $42 forward $63 $-1 #
edge $-1 -1 $-1 $66 0 $45 3.6197563775917776 $41 $67 forward @7 unknown #
coedge $-1 -1 $-1 $59 $68 $24 $44 reversed $36 $-1 #
edge $-1 -1 $-1 $66 0 $32 4.1864177885367599 $24 $69 forward @7 unknown #
vertex $-1 -1 $-1 $54 $70 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 -0.34842491355310223 0.063383917862424019 0.93519118824544256 I I #
coedge $-1 -1 $-1 $71 $27 $68 $72 reversed $49 $-1 #
coedge $-1 -1 $-1 $27 $71 $73 $74 reversed $49 $-1 #
loop $-1 -1 $-1 $-1 $27 $35 #
vertex $-1 -1 $-1 $30 $75 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 0.94477707880540274 -0.32771370335085087 0 I I #
straight-curve $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 -0.072682241539031203 -0.76763929572147338 -0.6367473623259875 I I #
coedge $-1 -1 $-1 $39 $41 $31 $54 forward $63 $-1 #
edge $-1 -1 $-1 $45 0 $33 3.8173156952508518 $53 $76 forward @7 unknown #
point $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 #
point $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 #
face $-1 -1 $-1 $77 $78 $2 $-1 $79 forward single #
plane-surface $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0 0 -1 0.075823670745747404 0.99712124185308604 0 forward_v I I I I #
coedge $-1 -1 $-1 $68 $43 $80 $81 reversed $36 $-1 #
coedge $-1 -1 $-1 $73 $82 $38 $61 reversed $83 $-1 #
edge $-1 -1 $-1 $50 0 $64 5.4498259321085127 $38 $84 forward @7 unknown #
coedge $-1 -1 $-1 $41 $39 $85 $86 reversed $63 $-1 #
loop $-1 -1 $-1 $-1 $53 $87 #
vertex $-1 -1 $-1 $86 $88 #
straight-curve $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 0.058940535127580275 0.99826149546041998 0 I I #
vertex $-1 -1 $-1 $86 $89 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.20585406555013996 -0.97858270151095494 0 I I #
coedge $-1 -1 $-1 $43 $59 $47 $72 forward $36 $-1 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 1.3877787807814457e-017 -0.87850377477042252 -0.47773540554800709 I I #
point $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 #
coedge $-1 -1 $-1 $48 $47 $90 $91 reversed $49 $-1 #
edge $-1 -1 $-1 $92 0 $32 2.567633724072949 $68 $93 forward @7 unknown #
coedge $-1 -1 $-1 $82 $60 $48 $74 forward $83 $-1 #
edge $-1 -1 $-1 $50 0 $94 4.9460245004234666 $73 $95 forward @7 unknown #
point $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 #
straight-curve $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 0.93252374204288202 0.36110866858376633 0 I I #
face $-1 -1 $-1 $87 $83 $2 $-1 $96 forward single #
loop $-1 -1 $-1 $-1 $97 $57 #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.26318198707465013 0.86293276999111279 -0.43137254914389711 0.03462186912272304 0.45529583038369054 0.88966681011133308 forward_v I I I I #
coedge $-1 -1 $-1 $97 $90 $59 $81 forward $78 $-1 #
edge $-1 -1 $-1 $92 0 $66 2.3910080886789973 $80 $98 forward @7 unknown #
coedge $-1 -1 $-1 $60 $73 $99 $100 reversed $83 $-1 #
loop $-1 -1 $-1 $-1 $60 $77 #
straight-curve $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0.070533239083480248 0.9275492765665786 0.36698419819552092 I I #
coedge $-1 -1 $-1 $99 $101 $62 $86 forward $102 $-1 #
edge $-1 -1 $-1 $66 0 $64 3.0092408855670816 $85 $103 forward @7 unknown #
face $-1 -1 $-1 $104 $63 $2 $-1 $105 forward single #
point $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 #
point $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 #
coedge $-1 -1 $-1 $80 $97 $71 $91 forward $78 $-1 #
edge $-1 -1 $-1 $94 0 $92 4.6883381143041722 $90 $106 forward @7 unknown #
vertex $-1 -1 $-1 $91 $107 #
straight-curve $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 0.22504944810139033 -0.9743473435635055 0 I I #
vertex $-1 -1 $-1 $100 $108 #
straight-curve $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0.26693459672279263 0.96371464711938482 0 I I #
plane-surface $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.86559381815832204 -0.23975658922117712 0.43961815236762641 -0.44509782675002491 0.033846386626385921 0.89484207921551284 forward_v I I I I #
coedge $-1 -1 $-1 $90 $80 $101 $109 reversed $78 $-1 #
straight-curve $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 0.24167402664387749 0.4918497504334145 0.83646726645118774 I I #
coedge $-1 -1 $-1 $101 $85 $82 $100 forward $102 $-1 #
edge $-1 -1 $-1 $64 0 $94 2.2268911813042807 $99 $110 forward @7 unknown #
coedge $-1 -1 $-1 $85 $99 $97 $109 forward $102 $-1 #
loop $-1 -1 $-1 $-1 $85 $104 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 0.98719168595608686 0.1595386322467959 0 I I #
face $-1 -1 $-1 $-1 $102 $2 $-1 $111 forward single #
plane-surface $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 0 0 1 -0.075823670745747404 -0.99712124185308604 0 forward_v I I I I #
straight-curve $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 -0.95650381999688194 -0.2917198010615189 0 I I #
point $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 #
point $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 #
edge $-1 -1 $-1 $94 0 $66 4.3929505707935217 $101 $112 forward @7 unknown #
straight-curve $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.42025905344000414 -0.12951950552997801 -0.89811303614243443 I I #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.15590940046942497 0.96473475883710602 -0.21208277614359863 0.016518332808874978 0.21722478431515085 0.97598183270000038 forward_v I I I I #
straight-curve $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 -0.88928129289971092 -0.043629976532672143 0.45527486999215883 I I #
End-of-ACIS-data 
"""

CUBE = """700 0 1 0 
@33 Open Design Alliance ACIS Builder @12 ACIS 32.0 NT @24 Sat Apr 23 14:35:11 2022 
1 9.9999999999999995e-007 1e-010 
body $1 -1 $-1 $2 $-1 $3 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $0 $4 $-1 #
lump $5 -1 $-1 $-1 $6 $0 #
transform $-1 -1 1 0 0 0 1 0 0 0 1 388.5 388.5 388.5 1 no_rotate no_reflect no_shear #
eye_refinement $-1 -1 @5 grid  1 @3 tri 1 @4 surf 0 @3 adj 0 @4 grad 0 @9 postcheck 0 @4 stol -5 @4 ntol 40 @4 dsil 0 @8 flatness 0 @7 pixarea 0 @4 hmax 0 @6 gridar 0 @5 mgrid 3000 @5 ugrid 0 @5 vgrid 0 @10 end_fields #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $2 $4 $-1 #
shell $7 -1 $-1 $-1 $-1 $8 $-1 $2 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $6 $4 $-1 #
face $9 -1 $-1 $10 $11 $6 $-1 $12 forward single #
fmesh-eye-attrib $-1 -1 $13 $-1 $8 #
face $14 -1 $-1 $15 $16 $6 $-1 $17 reversed single #
loop $-1 -1 $-1 $-1 $18 $8 #
plane-surface $-1 -1 $-1 0 0 388.5 0 0 1 1 0 0 forward_v I I I I #
ref_vt-eye-attrib $-1 -1 $-1 $9 $8 $4 $-1 #
fmesh-eye-attrib $-1 -1 $19 $-1 $10 #
face $20 -1 $-1 $21 $22 $6 $-1 $23 reversed single #
loop $-1 -1 $-1 $-1 $24 $10 #
plane-surface $-1 -1 $-1 0 0 -388.5 0 0 1 1 0 0 forward_v I I I I #
coedge $-1 -1 $-1 $25 $26 $27 $28 forward $11 $-1 #
ref_vt-eye-attrib $-1 -1 $-1 $14 $10 $4 $-1 #
fmesh-eye-attrib $-1 -1 $29 $-1 $15 #
face $30 -1 $-1 $31 $32 $6 $-1 $33 reversed single #
loop $-1 -1 $-1 $-1 $34 $15 #
plane-surface $-1 -1 $-1 0 -388.5 0 0 1 0 0 0 1 forward_v I I I I #
coedge $-1 -1 $-1 $35 $36 $37 $38 forward $16 $-1 #
coedge $-1 -1 $-1 $39 $18 $40 $41 forward $11 $-1 #
coedge $-1 -1 $-1 $18 $39 $42 $43 forward $11 $-1 #
coedge $-1 -1 $-1 $44 $45 $18 $28 reversed $46 $-1 #
edge $47 -1 $-1 $48 -388.5 $49 388.5 $27 $50 forward @7 unknown #
ref_vt-eye-attrib $-1 -1 $-1 $20 $15 $4 $-1 #
fmesh-eye-attrib $-1 -1 $51 $-1 $21 #
face $52 -1 $-1 $53 $54 $6 $-1 $55 reversed single #
loop $-1 -1 $-1 $-1 $56 $21 #
plane-surface $-1 -1 $-1 -388.5 0 0 1 0 0 0 0 -1 forward_v I I I I #
coedge $-1 -1 $-1 $57 $42 $58 $59 forward $22 $-1 #
coedge $-1 -1 $-1 $60 $24 $57 $61 forward $16 $-1 #
coedge $-1 -1 $-1 $24 $60 $62 $63 forward $16 $-1 #
coedge $-1 -1 $-1 $45 $44 $24 $38 reversed $46 $-1 #
edge $64 -1 $-1 $65 -388.5 $66 388.5 $37 $67 forward @7 unknown #
coedge $-1 -1 $-1 $26 $25 $68 $69 forward $11 $-1 #
coedge $-1 -1 $-1 $70 $71 $25 $41 reversed $54 $-1 #
edge $72 -1 $-1 $49 -388.5 $73 388.5 $40 $74 forward @7 unknown #
coedge $-1 -1 $-1 $34 $75 $26 $43 reversed $22 $-1 #
edge $76 -1 $-1 $77 -388.5 $48 388.5 $42 $78 forward @7 unknown #
coedge $-1 -1 $-1 $37 $27 $75 $79 forward $46 $-1 #
coedge $-1 -1 $-1 $27 $37 $70 $80 reversed $46 $-1 #
loop $-1 -1 $-1 $-1 $44 $53 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $28 #
vertex $-1 -1 $-1 $28 $81 #
vertex $-1 -1 $-1 $28 $82 #
straight-curve $-1 -1 $-1 388.5 0 388.5 0 1 0 I I #
ref_vt-eye-attrib $-1 -1 $-1 $30 $21 $4 $-1 #
fmesh-eye-attrib $-1 -1 $83 $-1 $31 #
face $84 -1 $-1 $-1 $46 $6 $-1 $85 reversed single #
loop $-1 -1 $-1 $-1 $70 $31 #
plane-surface $-1 -1 $-1 0 388.5 0 0 -1 0 0 0 -1 forward_v I I I I #
coedge $-1 -1 $-1 $86 $68 $71 $87 forward $32 $-1 #
coedge $-1 -1 $-1 $75 $34 $35 $61 reversed $22 $-1 #
coedge $-1 -1 $-1 $68 $86 $34 $59 reversed $32 $-1 #
edge $88 -1 $-1 $77 -388.5 $89 388.5 $58 $90 forward @7 unknown #
coedge $-1 -1 $-1 $36 $35 $86 $91 forward $16 $-1 #
edge $92 -1 $-1 $66 -388.5 $89 388.5 $57 $93 forward @7 unknown #
coedge $-1 -1 $-1 $71 $70 $36 $63 reversed $54 $-1 #
edge $94 -1 $-1 $95 -388.5 $65 388.5 $62 $96 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $38 #
vertex $-1 -1 $-1 $38 $97 #
vertex $-1 -1 $-1 $79 $98 #
straight-curve $-1 -1 $-1 388.5 0 -388.5 0 -1 0 I I #
coedge $-1 -1 $-1 $56 $58 $39 $69 reversed $32 $-1 #
edge $99 -1 $-1 $73 -388.5 $77 388.5 $68 $100 forward @7 unknown #
coedge $-1 -1 $-1 $62 $40 $45 $80 forward $54 $-1 #
coedge $-1 -1 $-1 $40 $62 $56 $87 reversed $54 $-1 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $41 #
vertex $-1 -1 $-1 $41 $101 #
straight-curve $-1 -1 $-1 0 388.5 388.5 -1 0 0 I I #
coedge $-1 -1 $-1 $42 $57 $44 $79 reversed $22 $-1 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $43 #
vertex $-1 -1 $-1 $69 $102 #
straight-curve $-1 -1 $-1 0 -388.5 388.5 1 0 0 I I #
edge $103 -1 $-1 $48 -388.5 $66 388.5 $44 $104 forward @7 unknown #
edge $105 -1 $-1 $49 -388.5 $65 388.5 $45 $106 forward @7 unknown #
point $-1 -1 $-1 388.5 -388.5 388.5 #
point $-1 -1 $-1 388.5 388.5 388.5 #
ref_vt-eye-attrib $-1 -1 $-1 $52 $31 $4 $-1 #
fmesh-eye-attrib $-1 -1 $107 $-1 $53 #
plane-surface $-1 -1 $-1 388.5 0 0 -1 0 0 0 0 1 forward_v I I I I #
coedge $-1 -1 $-1 $58 $56 $60 $91 reversed $32 $-1 #
edge $108 -1 $-1 $73 -388.5 $95 388.5 $71 $109 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $59 #
vertex $-1 -1 $-1 $91 $110 #
straight-curve $-1 -1 $-1 -388.5 -388.5 0 0 0 -1 I I #
edge $111 -1 $-1 $89 -388.5 $95 388.5 $86 $112 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $61 #
straight-curve $-1 -1 $-1 0 -388.5 -388.5 -1 0 0 I I #
ptlist-eye-attrib $-1 -1 $-1 $-1 $63 #
vertex $-1 -1 $-1 $63 $113 #
straight-curve $-1 -1 $-1 0 388.5 -388.5 1 0 0 I I #
point $-1 -1 $-1 388.5 388.5 -388.5 #
point $-1 -1 $-1 388.5 -388.5 -388.5 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $69 #
straight-curve $-1 -1 $-1 -388.5 0 388.5 0 -1 0 I I #
point $-1 -1 $-1 -388.5 388.5 388.5 #
point $-1 -1 $-1 -388.5 -388.5 388.5 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $79 #
straight-curve $-1 -1 $-1 388.5 -388.5 0 0 0 -1 I I #
ptlist-eye-attrib $-1 -1 $-1 $-1 $80 #
straight-curve $-1 -1 $-1 388.5 388.5 0 0 0 -1 I I #
ref_vt-eye-attrib $-1 -1 $-1 $84 $53 $4 $-1 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $87 #
straight-curve $-1 -1 $-1 -388.5 388.5 0 0 0 -1 I I #
point $-1 -1 $-1 -388.5 -388.5 -388.5 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $91 #
straight-curve $-1 -1 $-1 -388.5 0 -388.5 0 1 0 I I #
point $-1 -1 $-1 -388.5 388.5 -388.5 #
End-of-ACIS-data 
"""

if __name__ == "__main__":
    main()
