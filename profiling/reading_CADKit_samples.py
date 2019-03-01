import ezdxf
import glob
from collections import Counter
from datetime import datetime

CADKIT = r"D:\Source\dxftest\CADKitSamples\*.dxf"
FILE = r"D:\Source\dxftest\CADKitSamples\WOOD DETAILS.dxf"


def count_entities(msp):
    counter = Counter()
    for entity in msp:
        counter[entity.dxftype()] += 1
    return counter


for filename in glob.glob(CADKIT):
    print('reading file: {}'.format(filename))

    start_reading = datetime.now()
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    old_entities = count_entities(msp)
    old_count = len(msp)
    old_timing = datetime.now() - start_reading
    print('OLD: loaded {} entities in {} sec'.format(old_count, old_timing))

    start_reading = datetime.now()
    doc = ezdxf.readfile2(filename)
    msp = doc.modelspace()
    new_entities = count_entities(msp)
    new_count = len(msp)
    new_timing = datetime.now() - start_reading
    print('NEW: loaded {} entities in {} sec'.format(new_count, new_timing))
    print('ratio OLD/NEW = 1:{:.1f}'.format(new_timing/old_timing))

    if new_count != old_count:
        new_keys = set(new_entities.keys())
        old_keys = set(old_entities.keys())
        for key in sorted(new_keys | old_keys):
            n = new_entities[key]
            o = old_entities[key]
            if n != o:
                print('{}  NEW: {} OLD: {}'.format(key, n, o))
