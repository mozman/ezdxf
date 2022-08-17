#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import shapefile


def test_load_shp_file():
    shp = shapefile.shp_loads(TXT)
    assert shp.name == "TXT"
    assert shp.vector_length == 6
    assert shp.above == 6
    assert shp.below == 2
    assert shp.mode == shapefile.FontMode.VERTICAL
    assert shp.encoding == shapefile.FontEncoding.UNICODE
    assert shp.embed == shapefile.FontEmbedding.ALLOWED

    assert len(shp.symbols) == 5


TXT = """

;;type, size, name
*UNIFONT,6,TXT
;;above, below, mode, encode, embed, 0
6,2,2,0,0,0

;;shapenumber, defbytes, shapename
*0000A,7,lf
2,0AC,14,8,(9,10),0

*00020,7,spc
2,060,14,8,(-6,-8),0

*00041,21,uca
2,14,8,(-2,-6),1,024,043,04D,02C,2,047,1,040,2,02E,14,8,(-4,-3),
0

*00042,29,ucb
2,14,8,(-2,-6),1,030,012,014,016,028,2,020,1,012,014,016,038,2,
010,1,06C,2,050,14,8,(-4,-3),0

*00043,23,ucc
2,14,8,(-2,-6),040,014,1,01A,028,016,044,012,020,01E,2,02E,03C,
14,8,(-4,-3),0

"""

if __name__ == '__main__':
    pytest.main([__file__])
