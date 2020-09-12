import sys
import glob
import ezdxf
from ezdxf.audit import Auditor
from itertools import chain

DIR1 = r"D:\Source\dxftest\CADKitSamples\*.dxf"
DIR2 = r"D:\Source\dxftest\*.dxf"

def run(start):
    if start > 0:
        start -= 1
    names = list(chain(glob.glob(DIR1), glob.glob(DIR2)))
    names = names[start:]
    count = 0
    for filename in names:
        count += 1
        print("processing: {}/{} file: {}".format(count+start, len(names)+start, filename))
        doc = ezdxf.readfile(filename)

        auditor = Auditor(doc)
        if len(auditor):
            auditor.print_error_report(auditor.errors)


if __name__ == '__main__':
    try:
        start = sys.argv[1]
    except IndexError:
        start = 0
    run(int(start))
