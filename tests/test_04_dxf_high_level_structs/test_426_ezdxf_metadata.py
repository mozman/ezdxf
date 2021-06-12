#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.document import CREATED_BY_EZDXF, WRITTEN_BY_EZDXF


R12 = ezdxf.new("R12")
R2000 = ezdxf.new("R2000")


@pytest.mark.parametrize("doc", [R12, R2000])
def test_created_by_ezdxf_metadata(doc):
    metadata = doc.ezdxf_metadata()
    assert metadata[CREATED_BY_EZDXF].startswith(ezdxf.__version__)


@pytest.mark.parametrize("doc", [R12, R2000])
def test_written_by_ezdxf_metadata(doc, tmp_path):
    doc.saveas(tmp_path / "ez.dxf")
    metadata = doc.ezdxf_metadata()
    assert metadata[WRITTEN_BY_EZDXF].startswith(ezdxf.__version__)


if __name__ == '__main__':
    pytest.main([__file__])
