# Created: 01.05.2014, 2018 rewritten for pytest
# Copyright (C) 2014-2019, Manfred Moitzi
# License: MIT License
from ezdxf.tools.crypt import decode, encode


def test_decode():
    for enc, dec in zip(decode(ENCODED_LINES), DECODED_LINES):
        assert dec == enc


def test_encode():
    for enc, dec in zip(ENCODED_LINES, encode(DECODED_LINES)):
        assert enc == dec


DECODED_LINES = r"""21200 115 2 26
16 Autodesk AutoCAD 19 ASM 217.0.0.4503 NT 0
1 9.9999999999999995e-007 1e-010
asmheader $-1 -1 @12 217.0.0.4503 #
body $2 -1 $-1 $3 $-1 $-1 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $1 $4 $5 #
lump $6 -1 $-1 $-1 $7 $1 #
eye_refinement $-1 -1 @5 grid  1 @3 tri 1 @4 surf 0 @3 adj 0 @4 grad 0 @9 postcheck 0 @4 stol 0.020115179941058159 @4 ntol 30 @4 dsil 0 @8 flatness 0 @7 pixarea 0 @4 hmax 0 @6 gridar 0 @5 mgrid 3000 @5 ugrid 0 @5 vgrid 0 @10 end_fields #
vertex_template $-1 -1 3 0 1 8 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $3 $4 $5 #
shell $8 -1 $-1 $-1 $-1 $9 $-1 $3 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $7 $4 $5 #
face $10 -1 $-1 $11 $12 $7 $-1 $13 forward single #
fmesh-eye-attrib $-1 -1 $14 $-1 $9 #
face $15 -1 $-1 $16 $17 $7 $-1 $18 reversed single #
loop $-1 -1 $-1 $-1 $19 $9 #
plane-surface $-1 -1 $-1 5 5 10 0 0 1 1 0 0 forward_v I I I I #
ref_vt-eye-attrib $-1 -1 $-1 $10 $9 $4 $5 #
fmesh-eye-attrib $-1 -1 $20 $-1 $11 #
face $21 -1 $-1 $22 $23 $7 $-1 $24 reversed single #
loop $-1 -1 $-1 $-1 $25 $11 #
plane-surface $-1 -1 $-1 5 5 0 0 0 1 1 0 0 forward_v I I I I #
coedge $-1 -1 $-1 $26 $27 $28 $29 forward $12 $-1 #
ref_vt-eye-attrib $-1 -1 $-1 $15 $11 $4 $5 #
fmesh-eye-attrib $-1 -1 $30 $-1 $16 #
face $31 -1 $-1 $32 $33 $7 $-1 $34 reversed single #
loop $-1 -1 $-1 $-1 $35 $16 #
plane-surface $-1 -1 $-1 5 0 5 0 1 0 0 0 1 forward_v I I I I #
coedge $-1 -1 $-1 $36 $37 $38 $39 forward $17 $-1 #
coedge $-1 -1 $-1 $40 $19 $41 $42 forward $12 $-1 #
coedge $-1 -1 $-1 $19 $40 $43 $44 forward $12 $-1 #
coedge $-1 -1 $-1 $45 $46 $19 $29 reversed $47 $-1 #
edge $48 -1 $-1 $49 -5 $50 5 $28 $51 forward @7 unknown #
ref_vt-eye-attrib $-1 -1 $-1 $21 $16 $4 $5 #
fmesh-eye-attrib $-1 -1 $52 $-1 $22 #
face $53 -1 $-1 $54 $55 $7 $-1 $56 reversed single #
loop $-1 -1 $-1 $-1 $57 $22 #
plane-surface $-1 -1 $-1 0 5 5 1 0 0 0 0 -1 forward_v I I I I #
coedge $-1 -1 $-1 $58 $43 $59 $60 forward $23 $-1 #
coedge $-1 -1 $-1 $61 $25 $58 $62 forward $17 $-1 #
coedge $-1 -1 $-1 $25 $61 $63 $64 forward $17 $-1 #
coedge $-1 -1 $-1 $46 $45 $25 $39 reversed $47 $-1 #
edge $65 -1 $-1 $66 -5 $67 5 $38 $68 forward @7 unknown #
coedge $-1 -1 $-1 $27 $26 $69 $70 forward $12 $-1 #
coedge $-1 -1 $-1 $71 $72 $26 $42 reversed $55 $-1 #
edge $73 -1 $-1 $50 -5 $74 5 $41 $75 forward @7 unknown #
coedge $-1 -1 $-1 $35 $76 $27 $44 reversed $23 $-1 #
edge $77 -1 $-1 $78 -5 $49 5 $43 $79 forward @7 unknown #
coedge $-1 -1 $-1 $38 $28 $76 $80 forward $47 $-1 #
coedge $-1 -1 $-1 $28 $38 $71 $81 reversed $47 $-1 #
loop $-1 -1 $-1 $-1 $45 $54 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $29 #
vertex $-1 -1 $-1 $29 0 $82 #
vertex $-1 -1 $-1 $29 1 $83 #
straight-curve $-1 -1 $-1 10 5 10 0 1 0 I I #
ref_vt-eye-attrib $-1 -1 $-1 $31 $22 $4 $5 #
fmesh-eye-attrib $-1 -1 $84 $-1 $32 #
face $85 -1 $-1 $-1 $47 $7 $-1 $86 reversed single #
loop $-1 -1 $-1 $-1 $71 $32 #
plane-surface $-1 -1 $-1 5 10 5 0 -1 0 0 0 -1 forward_v I I I I #
coedge $-1 -1 $-1 $87 $69 $72 $88 forward $33 $-1 #
coedge $-1 -1 $-1 $76 $35 $36 $62 reversed $23 $-1 #
coedge $-1 -1 $-1 $69 $87 $35 $60 reversed $33 $-1 #
edge $89 -1 $-1 $78 -5 $90 5 $59 $91 forward @7 unknown #
coedge $-1 -1 $-1 $37 $36 $87 $92 forward $17 $-1 #
edge $93 -1 $-1 $67 -5 $90 5 $58 $94 forward @7 unknown #
coedge $-1 -1 $-1 $72 $71 $37 $64 reversed $55 $-1 #
edge $95 -1 $-1 $96 -5 $66 5 $63 $97 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $39 #
vertex $-1 -1 $-1 $39 0 $98 #
vertex $-1 -1 $-1 $80 1 $99 #
straight-curve $-1 -1 $-1 10 5 0 0 -1 0 I I #
coedge $-1 -1 $-1 $57 $59 $40 $70 reversed $33 $-1 #
edge $100 -1 $-1 $74 -5 $78 5 $69 $101 forward @7 unknown #
coedge $-1 -1 $-1 $63 $41 $46 $81 forward $55 $-1 #
coedge $-1 -1 $-1 $41 $63 $57 $88 reversed $55 $-1 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $42 #
vertex $-1 -1 $-1 $42 1 $102 #
straight-curve $-1 -1 $-1 5 10 10 -1 0 0 I I #
coedge $-1 -1 $-1 $43 $58 $45 $80 reversed $23 $-1 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $44 #
vertex $-1 -1 $-1 $70 1 $103 #
straight-curve $-1 -1 $-1 5 0 10 1 0 0 I I #
edge $104 -1 $-1 $49 -5 $67 5 $45 $105 forward @7 unknown #
edge $106 -1 $-1 $50 -5 $66 5 $46 $107 forward @7 unknown #
point $-1 -1 $-1 10 0 10 #
point $-1 -1 $-1 10 10 10 #
ref_vt-eye-attrib $-1 -1 $-1 $53 $32 $4 $5 #
fmesh-eye-attrib $-1 -1 $108 $-1 $54 #
plane-surface $-1 -1 $-1 10 5 5 -1 0 0 0 0 1 forward_v I I I I #
coedge $-1 -1 $-1 $59 $57 $61 $92 reversed $33 $-1 #
edge $109 -1 $-1 $74 -5 $96 5 $72 $110 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $60 #
vertex $-1 -1 $-1 $92 0 $111 #
straight-curve $-1 -1 $-1 0 0 5 0 0 -1 I I #
edge $112 -1 $-1 $90 -5 $96 5 $87 $113 forward @7 unknown #
ptlist-eye-attrib $-1 -1 $-1 $-1 $62 #
straight-curve $-1 -1 $-1 5 0 0 -1 0 0 I I #
ptlist-eye-attrib $-1 -1 $-1 $-1 $64 #
vertex $-1 -1 $-1 $64 0 $114 #
straight-curve $-1 -1 $-1 5 10 0 1 0 0 I I #
point $-1 -1 $-1 10 10 0 #
point $-1 -1 $-1 10 0 0 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $70 #
straight-curve $-1 -1 $-1 0 5 10 0 -1 0 I I #
point $-1 -1 $-1 0 10 10 #
point $-1 -1 $-1 0 0 10 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $80 #
straight-curve $-1 -1 $-1 10 0 5 0 0 -1 I I #
ptlist-eye-attrib $-1 -1 $-1 $-1 $81 #
straight-curve $-1 -1 $-1 10 10 5 0 0 -1 I I #
ref_vt-eye-attrib $-1 -1 $-1 $85 $54 $4 $5 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $88 #
straight-curve $-1 -1 $-1 0 10 5 0 0 -1 I I #
point $-1 -1 $-1 0 0 0 #
ptlist-eye-attrib $-1 -1 $-1 $-1 $92 #
straight-curve $-1 -1 $-1 0 5 0 0 1 0 I I #
point $-1 -1 $-1 0 10 0 #
""".splitlines()

ENCODED_LINES = r"""mnmoo nnj m mi
ni ^ *+0;:,4 ^ *+0\^ [ nf ^ LR mnhqoqoqkjol QK o
n fqfffffffffffffffj:rooh n:rono
>,27:>;:- {rn rn _nm mnhqoqoqkjol |
=0;& {m rn {rn {l {rn {rn |
-:9@)+r:&:r>++-6= {rn rn {rn {rn {n {k {j |
3*2/ {i rn {rn {rn {h {n |
:&:@-:961:2:1+ {rn rn _j 8-6;  n _l +-6 n _k ,*-9 o _l >;5 o _k 8->; o _f /0,+<7:<4 o _k ,+03 oqomonnjnhffknojgnjf _k 1+03 lo _k ;,63 o _g 93>+1:,, o _h /6'>-:> o _k 72>' o _i 8-6;>- o _j 28-6; looo _j *8-6; o _j )8-6; o _no :1;@96:3;, |
):-+:'@+:2/3>+: {rn rn l o n g |
-:9@)+r:&:r>++-6= {rn rn {rn {rn {l {k {j |
,7:33 {g rn {rn {rn {rn {f {rn {l |
-:9@)+r:&:r>++-6= {rn rn {rn {rn {h {k {j |
9><: {no rn {rn {nn {nm {h {rn {nl 90-(>-; ,6183: |
92:,7r:&:r>++-6= {rn rn {nk {rn {f |
9><: {nj rn {rn {ni {nh {h {rn {ng -:):-,:; ,6183: |
300/ {rn rn {rn {rn {nf {f |
/3>1:r,*-9><: {rn rn {rn j j no o o n n o o 90-(>-;@) V V V V |
-:9@)+r:&:r>++-6= {rn rn {rn {no {f {k {j |
92:,7r:&:r>++-6= {rn rn {mo {rn {nn |
9><: {mn rn {rn {mm {ml {h {rn {mk -:):-,:; ,6183: |
300/ {rn rn {rn {rn {mj {nn |
/3>1:r,*-9><: {rn rn {rn j j o o o n n o o 90-(>-;@) V V V V |
<0:;8: {rn rn {rn {mi {mh {mg {mf 90-(>-; {nm {rn |
-:9@)+r:&:r>++-6= {rn rn {rn {nj {nn {k {j |
92:,7r:&:r>++-6= {rn rn {lo {rn {ni |
9><: {ln rn {rn {lm {ll {h {rn {lk -:):-,:; ,6183: |
300/ {rn rn {rn {rn {lj {ni |
/3>1:r,*-9><: {rn rn {rn j o j o n o o o n 90-(>-;@) V V V V |
<0:;8: {rn rn {rn {li {lh {lg {lf 90-(>-; {nh {rn |
<0:;8: {rn rn {rn {ko {nf {kn {km 90-(>-; {nm {rn |
<0:;8: {rn rn {rn {nf {ko {kl {kk 90-(>-; {nm {rn |
<0:;8: {rn rn {rn {kj {ki {nf {mf -:):-,:; {kh {rn |
:;8: {kg rn {rn {kf rj {jo j {mg {jn 90-(>-; _h *1410(1 |
-:9@)+r:&:r>++-6= {rn rn {rn {mn {ni {k {j |
92:,7r:&:r>++-6= {rn rn {jm {rn {mm |
9><: {jl rn {rn {jk {jj {h {rn {ji -:):-,:; ,6183: |
300/ {rn rn {rn {rn {jh {mm |
/3>1:r,*-9><: {rn rn {rn o j j n o o o o rn 90-(>-;@) V V V V |
<0:;8: {rn rn {rn {jg {kl {jf {io 90-(>-; {ml {rn |
<0:;8: {rn rn {rn {in {mj {jg {im 90-(>-; {nh {rn |
<0:;8: {rn rn {rn {mj {in {il {ik 90-(>-; {nh {rn |
<0:;8: {rn rn {rn {ki {kj {mj {lf -:):-,:; {kh {rn |
:;8: {ij rn {rn {ii rj {ih j {lg {ig 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {mh {mi {if {ho 90-(>-; {nm {rn |
<0:;8: {rn rn {rn {hn {hm {mi {km -:):-,:; {jj {rn |
:;8: {hl rn {rn {jo rj {hk j {kn {hj 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {lj {hi {mh {kk -:):-,:; {ml {rn |
:;8: {hh rn {rn {hg rj {kf j {kl {hf 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {lg {mg {hi {go 90-(>-; {kh {rn |
<0:;8: {rn rn {rn {mg {lg {hn {gn -:):-,:; {kh {rn |
300/ {rn rn {rn {rn {kj {jk |
/+36,+r:&:r>++-6= {rn rn {rn {rn {mf |
):-+:' {rn rn {rn {mf o {gm |
):-+:' {rn rn {rn {mf n {gl |
,+->687+r<*-): {rn rn {rn no j no o n o V V |
-:9@)+r:&:r>++-6= {rn rn {rn {ln {mm {k {j |
92:,7r:&:r>++-6= {rn rn {gk {rn {lm |
9><: {gj rn {rn {rn {kh {h {rn {gi -:):-,:; ,6183: |
300/ {rn rn {rn {rn {hn {lm |
/3>1:r,*-9><: {rn rn {rn j no j o rn o o o rn 90-(>-;@) V V V V |
<0:;8: {rn rn {rn {gh {if {hm {gg 90-(>-; {ll {rn |
<0:;8: {rn rn {rn {hi {lj {li {im -:):-,:; {ml {rn |
<0:;8: {rn rn {rn {if {gh {lj {io -:):-,:; {ll {rn |
:;8: {gf rn {rn {hg rj {fo j {jf {fn 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {lh {li {gh {fm 90-(>-; {nh {rn |
:;8: {fl rn {rn {ih rj {fo j {jg {fk 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {hm {hn {lh {ik -:):-,:; {jj {rn |
:;8: {fj rn {rn {fi rj {ii j {il {fh 90-(>-; _h *1410(1 |
/+36,+r:&:r>++-6= {rn rn {rn {rn {lf |
):-+:' {rn rn {rn {lf o {fg |
):-+:' {rn rn {rn {go n {ff |
,+->687+r<*-): {rn rn {rn no j o o rn o V V |
<0:;8: {rn rn {rn {jh {jf {ko {ho -:):-,:; {ll {rn |
:;8: {noo rn {rn {hk rj {hg j {if {non 90-(>-; _h *1410(1 |
<0:;8: {rn rn {rn {il {kn {ki {gn 90-(>-; {jj {rn |
<0:;8: {rn rn {rn {kn {il {jh {gg -:):-,:; {jj {rn |
/+36,+r:&:r>++-6= {rn rn {rn {rn {km |
):-+:' {rn rn {rn {km n {nom |
,+->687+r<*-): {rn rn {rn j no no rn o o V V |
<0:;8: {rn rn {rn {kl {jg {kj {go -:):-,:; {ml {rn |
/+36,+r:&:r>++-6= {rn rn {rn {rn {kk |
):-+:' {rn rn {rn {ho n {nol |
,+->687+r<*-): {rn rn {rn j o no n o o V V |
:;8: {nok rn {rn {kf rj {ih j {kj {noj 90-(>-; _h *1410(1 |
:;8: {noi rn {rn {jo rj {ii j {ki {noh 90-(>-; _h *1410(1 |
/061+ {rn rn {rn no o no |
/061+ {rn rn {rn no no no |
-:9@)+r:&:r>++-6= {rn rn {rn {jl {lm {k {j |
92:,7r:&:r>++-6= {rn rn {nog {rn {jk |
/3>1:r,*-9><: {rn rn {rn no j j rn o o o o n 90-(>-;@) V V V V |
<0:;8: {rn rn {rn {jf {jh {in {fm -:):-,:; {ll {rn |
:;8: {nof rn {rn {hk rj {fi j {hm {nno 90-(>-; _h *1410(1 |
/+36,+r:&:r>++-6= {rn rn {rn {rn {io |
):-+:' {rn rn {rn {fm o {nnn |
,+->687+r<*-): {rn rn {rn o o j o o rn V V |
:;8: {nnm rn {rn {fo rj {fi j {gh {nnl 90-(>-; _h *1410(1 |
/+36,+r:&:r>++-6= {rn rn {rn {rn {im |
,+->687+r<*-): {rn rn {rn j o o rn o o V V |
/+36,+r:&:r>++-6= {rn rn {rn {rn {ik |
):-+:' {rn rn {rn {ik o {nnk |
,+->687+r<*-): {rn rn {rn j no o n o o V V |
/061+ {rn rn {rn no no o |
/061+ {rn rn {rn no o o |
/+36,+r:&:r>++-6= {rn rn {rn {rn {ho |
,+->687+r<*-): {rn rn {rn o j no o rn o V V |
/061+ {rn rn {rn o no no |
/061+ {rn rn {rn o o no |
/+36,+r:&:r>++-6= {rn rn {rn {rn {go |
,+->687+r<*-): {rn rn {rn no o j o o rn V V |
/+36,+r:&:r>++-6= {rn rn {rn {rn {gn |
,+->687+r<*-): {rn rn {rn no no j o o rn V V |
-:9@)+r:&:r>++-6= {rn rn {rn {gj {jk {k {j |
/+36,+r:&:r>++-6= {rn rn {rn {rn {gg |
,+->687+r<*-): {rn rn {rn o no j o o rn V V |
/061+ {rn rn {rn o o o |
/+36,+r:&:r>++-6= {rn rn {rn {rn {fm |
,+->687+r<*-): {rn rn {rn o j o o n o V V |
/061+ {rn rn {rn o no o |
""".splitlines()
