#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.tools.text import MTextParser
from ezdxf.addons import MTextExplode

TEXT = r"{\fDIN OT|b0|i0|c0|p34;Abbruch Infoschild\PNotaus Einbindung\P\pxi-3,l4,t4;ehem.^IStaubsauger}"


def test_parse_text():
    result = list(MTextParser(TEXT))
    assert len(result) == 11


def test_explode_mtext():
    doc = ezdxf.new()
    msp = doc.modelspace()

    mtext = msp.add_mtext(TEXT)
    mtext.text = TEXT
    explode = MTextExplode(msp)
    explode.explode(mtext, destroy=True)
    assert len(msp) == 7


if __name__ == "__main__":
    pytest.main([__file__])
