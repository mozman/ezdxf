#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from io import StringIO
from time import sleep
import ezdxf


def doc2str(doc):
    stream = StringIO()
    doc.write(stream)
    return stream.getvalue()


@pytest.mark.parametrize("version", ["R12", "R2000", "R2018"])
def test_fixed_meta_data(version):
    ezdxf.options.write_fixed_meta_data_for_testing = True
    doc = ezdxf.new(version)
    txt1 = doc2str(doc)
    # write it again
    sleep(0.1)
    txt2 = doc2str(doc)
    assert txt1 == txt2


@pytest.mark.parametrize("version", ["R12", "R2000", "R2018"])
def test_meta_data_is_different(version):
    ezdxf.options.write_fixed_meta_data_for_testing = False
    doc = ezdxf.new(version)
    txt1 = doc2str(doc)
    # write it again
    sleep(0.1)
    txt2 = doc2str(doc)
    assert txt1 != txt2


if __name__ == '__main__':
    pytest.main([__file__])
