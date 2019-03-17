import ezdxf
from pathlib import Path
import datetime
from pympler import tracker
import logging

logging.basicConfig(filename=r"C:\Users\manfred\Desktop\Outbox\ezdxf-log.txt", level='INFO')
logger = logging.getLogger('ezdxf')

R12_FILES = r"D:\Source\dxftest\R12_test_files"
FILE = r"D:\Source\dxftest\CADKitSamples\WOOD DETAILS.dxf"
outpath = Path(r"C:\Users\manfred\Desktop\Outbox")

DXFTEST_PATH = Path(r'D:\Source\dxftest')

CADKIT_FILES = [
    r"CADKitSamples\A_000217.dxf",  # 0
    r"CADKitSamples\AEC Plan Elev Sample.dxf",  # 1
    r"CADKitSamples\backhoe.dxf",  # 2
    r"CADKitSamples\BIKE.DXF",  # 3
    r"CADKitSamples\cnc machine.dxf",  # 4
    r"CADKitSamples\Controller-M128-top.dxf",  # 5
    r"CADKitSamples\drilling_machine.dxf",  # 6
    r"CADKitSamples\fanuc-430-arm.dxf",  # 7
    r"CADKitSamples\Floor plan.dxf",  # 8
    r"CADKitSamples\gekko.DXF",  # 9
    r"CADKitSamples\house design for two family with comman staircasedwg.dxf",  # 10
    r"CADKitSamples\house design.dxf",  # 11
    r"CADKitSamples\kit-dev-coldfire-xilinx_5213.dxf",  # 12
    r"CADKitSamples\Laurana50k.dxf",  # 13
    r"CADKitSamples\Lock-Off.dxf",  # 14
    r"CADKitSamples\Mc Cormik-D3262.DXF",  # 15
    r"CADKitSamples\Mechanical Sample.dxf",  # 16
    r"CADKitSamples\Nikon_D90_Camera.DXF",  # 17
    r"CADKitSamples\pic_programmer.dxf",  # 18
    r"CADKitSamples\Proposed Townhouse.dxf",  # 19
    r"CADKitSamples\Shapefont.dxf",  # 20
    r"CADKitSamples\SMA-Controller.dxf",  # 21
    r"CADKitSamples\Tamiya TT-01.DXF",  # 22
    r"CADKitSamples\torso_uniform.dxf",  # 23
    r"CADKitSamples\Tyrannosaurus.DXF",  # 24
    r"CADKitSamples\WOOD DETAILS.dxf",  # 25
]


AUTODESK_FILES = [
    r"AutodeskProducts\Civil3D_2018.dxf",
    r"AutodeskProducts\Map3D_2017.dxf",
    r"AutodeskSamples\architectural_-_annotation_scaling_and_multileaders.dxf",
    r"AutodeskSamples\architectural_example-imperial.dxf",
    r"AutodeskSamples\blocks_and_tables_-_imperial.dxf",
    r"AutodeskSamples\blocks_and_tables_-_metric.dxf",
    r"AutodeskSamples\civil_example-imperial.dxf",
    r"AutodeskSamples\colorwh.dxf",
    r"AutodeskSamples\lineweights.dxf",
    r"AutodeskSamples\mechanical_example-imperial.dxf",
    r"AutodeskSamples\plot_screening_and_fill_patterns.dxf",
    r"AutodeskSamples\tablet.dxf",
    r"AutodeskSamples\title_block-ansi.dxf",
    r"AutodeskSamples\title_block-arch.dxf",
    r"AutodeskSamples\title_block-iso.dxf",
    r"AutodeskSamples\truetype.dxf",
    r"AutodeskSamples\visualization_-_aerial.dxf",
    r"AutodeskSamples\visualization_-_condominium_with_skylight.dxf",
    r"AutodeskSamples\visualization_-_conference_room.dxf",
    r"AutodeskSamples\visualization_-_sun_and_sky_demo.dxf",
]


def outname(fname: Path) -> Path:
    name = Path(fname).stem + '_ezdxf.dxf'
    return outpath / name


SEP_LINE = '-----------------------------------------------------------------------'

for filename in CADKIT_FILES[:5]:
    filename = DXFTEST_PATH / filename
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
