import ezdxf
from ezdxf.math import Matrix44, TransformError
from ezdxf.layouts import BaseLayout
from pathlib import Path

DIR = Path("~/Desktop/Outbox").expanduser()
EXAMPLE = ezdxf.options.test_files_path / "CADKitSamples" / "AEC Plan Elev Sample.dxf"


def transform_layout(layout: BaseLayout, m: Matrix44) -> None:
    for entity in layout:
        try:
            entity.transform(m)
        except (NotImplementedError, TransformError):
            pass


doc = ezdxf.readfile(EXAMPLE)
INCH_TO_MM = 25.4
transform_layout(doc.modelspace(), Matrix44.scale(INCH_TO_MM))
doc.saveas(DIR / "scaled.dxf")
