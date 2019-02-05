# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import datetime


def load_3D_model():
    import ezdxf
    dwg = ezdxf.readfile(filename=r"D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf")
    del dwg


def iter_3D_model():
    import ezdxf
    dwg = ezdxf.readfile(filename=r"D:\Source\dxftest\CADKitSamples\fanuc-430-arm.dxf")
    msp = dwg.modelspace()
    count = 0
    for e in msp:
        e.dxftype()
        count += 1
    print('Iterated {} entities in modelspace (fanuc-430-arm.dxf).'.format(count))
    del dwg


def load_2D_plan():
    import ezdxf
    dwg = ezdxf.readfile(filename=r"D:\Source\dxftest\CADKitSamples\AEC Plan Elev Sample.dxf")
    del dwg


def iter_2D_plan():
    import ezdxf
    dwg = ezdxf.readfile(filename=r"D:\Source\dxftest\CADKitSamples\AEC Plan Elev Sample.dxf")
    msp = dwg.modelspace()
    count = 0
    for e in msp:
        e.dxftype()
        count += 1
    print('Iterated {} entities in modelspace (AEC Plan Elev Sample.dxf).'.format(count))
    del dwg


def print_result(time, text):
    print("Operation: {} takes {} seconds".format(time, text))


def run(func):
    start = datetime.datetime.now()
    func()
    end = datetime.datetime.now()
    return end - start


if __name__ == '__main__':
    print_result(run(load_3D_model), 'load "faunc-430-arm.dxf"')
    print_result(run(iter_3D_model), 'iter "faunc-430-arm.dxf"')
    print_result(run(load_2D_plan), 'load "AEC Plan Elev Sample.dxf"')
    print_result(run(iter_2D_plan), 'iter "AEC Plan Elev Sample.dxf"')
