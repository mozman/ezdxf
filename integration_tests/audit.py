import sys
import glob
import ezdxf
from ezdxf.audit import Auditor
from itertools import chain

DIR1 = r"D:\Source\dxftest\CADKitSamples\*.dxf"
DIR2 = r"D:\Source\dxftest\*.dxf"
LEGACY_MODE = False


def run(start):
    if start > 0:
        start -= 1
    names = list(chain(glob.glob(DIR1), glob.glob(DIR2)))
    names = names[start:]
    count = 0
    for filename in names:
        count += 1
        print("processing: {}/{} file: {}".format(count+start, len(names)+start, filename))
        doc = ezdxf.readfile(filename, legacy_mode=LEGACY_MODE)

        auditor = Auditor(doc)
        errors = list(auditor.filter_zero_pointers(auditor.run()))
        if len(errors):
            auditor.print_error_report(errors)


if __name__ == '__main__':
    try:
        start = sys.argv[1]
    except IndexError:
        start = 0
    run(int(start))
