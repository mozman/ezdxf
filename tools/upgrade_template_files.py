__author__ = 'manfred'

import ezdxf


def add_appids(dwg):
    if "HATCHBACKGROUNDCOLOR" not in dwg.appids:
        dwg.appids.new("HATCHBACKGROUNDCOLOR", {'flags': 0})


PATH = r"C:\Users\manfred\Desktop\inbox\{}.dxf"


def main():
    for version in ("AC1015", "AC1018", "AC1021", "AC1024", "AC1027"):
        dwg = ezdxf.readfile(PATH.format(version))
        add_appids(dwg)
        dwg.save()

if __name__ == '__main__':
    main()