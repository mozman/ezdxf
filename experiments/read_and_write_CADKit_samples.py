import ezdxf
from pathlib import Path
import datetime
from pympler import tracker
import logging

logging.basicConfig(filename=r"C:\Users\manfred\Desktop\Outbox\CADKit-log.txt", level='INFO')
logger = logging.getLogger('ezdxf')

R12_FILES = r"D:\Source\dxftest\R12_test_files"
FILE = r"D:\Source\dxftest\CADKitSamples\WOOD DETAILS.dxf"
outpath = Path(r"C:\Users\manfred\Desktop\Outbox")

CADKIT = Path(r"D:\Source\dxftest\CADKitSamples")
CADKIT_FILES = [
    "A_000217.dxf",  # 0
    "AEC Plan Elev Sample.dxf",  # 1
    "backhoe.dxf",  # 2
    "BIKE.DXF",  # 3
    "cnc machine.dxf",  # 4
    "Controller-M128-top.dxf",  # 5
    "drilling_machine.dxf",  # 6
    "fanuc-430-arm.dxf",  # 7
    "Floor plan.dxf",  # 8
    "gekko.DXF",  # 9
    "house design for two family with comman staircasedwg.dxf",  # 10
    "house design.dxf",  # 11
    "kit-dev-coldfire-xilinx_5213.dxf",  # 12
    "Laurana50k.dxf",  # 13
    "Lock-Off.dxf",  # 14
    "Mc Cormik-D3262.DXF",  # 15
    "Mechanical Sample.dxf",  # 16
    "Nikon_D90_Camera.DXF",  # 17
    "pic_programmer.dxf",  # 18
    "Proposed Townhouse.dxf",  # 19
    "Shapefont.dxf",  # 20
    "SMA-Controller.dxf",  # 21
    "Tamiya TT-01.DXF",  # 22
    "torso_uniform.dxf",  # 23
    "Tyrannosaurus.DXF",  # 24
    "WOOD DETAILS.dxf",  # 25
]


def outname(fname: Path) -> Path:
    name = Path(fname).stem + '_ezdxf.dxf'
    return outpath / name


SEP_LINE = '-----------------------------------------------------------------------'

for filename in CADKIT_FILES[:3]:
    filename = CADKIT / filename
    new_name = outname(filename)
    if not new_name.exists():
        logging.info('processing file: {}'.format(filename))
        logging.info(SEP_LINE)
        print('reading file: {}'.format(filename), end=' ')
        # tr1 = tracker.SummaryTracker()
        start = datetime.datetime.now()
        doc = ezdxf.readfile(str(filename), legacy_mode=False)
        end = datetime.datetime.now()
        # tr1.print_diff()
        print(' ... in {:.1f} sec'.format((end - start).total_seconds()))
        print('writing file: {}'.format(new_name), end=' ')
        start = datetime.datetime.now()
        doc.saveas(new_name)
        end = datetime.datetime.now()
        print(' ... in {:.1f} sec\n'.format((end - start).total_seconds()))

logging.shutdown()
