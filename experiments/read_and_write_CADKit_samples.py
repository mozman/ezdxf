import ezdxf
from pathlib import Path
import datetime

CADKIT_PATH = r"D:\Source\dxftest\CADKitSamples"
R12_FILES = r"D:\Source\dxftest\R12_test_files"
FILE = r"D:\Source\dxftest\CADKitSamples\WOOD DETAILS.dxf"
outpath = Path(r"C:\Users\manfred\Desktop\Outbox")


def outname(fname: Path) -> Path:
    name = fname.stem + '_ezdxf.dxf'
    return outpath / name


for filename in Path(CADKIT_PATH).glob('*.dxf'):
    new_name = outname(filename)
    if not new_name.exists():
        print('reading file: {}'.format(filename))
        start = datetime.datetime.now()
        doc = ezdxf.readfile2(str(filename), legacy_mode=False)
        end = datetime.datetime.now()
        print(' ... in {:.1f} sec'.format((end-start).total_seconds()))

        print('writing file: {}'.format(new_name))
        start = datetime.datetime.now()
        doc.saveas(new_name)
        end = datetime.datetime.now()
        print(' ... in {:.1f} sec'.format((end - start).total_seconds()))
