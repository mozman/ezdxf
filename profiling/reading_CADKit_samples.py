import ezdxf
import glob

from datetime import datetime

DIR1 = r"D:\Source\dxftest\CADKitSamples\*.dxf"

start_time = datetime.now()

for filename in glob.glob(DIR1):
    print('reading file: {}'.format(filename))
    start_reading = datetime.now()
    doc = ezdxf.readfile2(filename)
    count = len(doc.modelspace())
    nes_timing = datetime.now() - start_reading
    print('NES: reading {} entities in modelspace takes {} seconds.'.format(count, nes_timing))
    start_reading = datetime.now()
    doc = ezdxf.readfile(filename)
    count = len(doc.modelspace())
    oes_timing = datetime.now() - start_reading
    print('OES: reading {} entities in modelspace takes {} seconds.'.format(count, oes_timing))
    print('ratio OES/NES = {}'.format(oes_timing/nes_timing))



