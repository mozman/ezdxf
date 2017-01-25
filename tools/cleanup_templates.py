__author__ = 'manfred'

import ezdxf



PATH = r"C:\Users\manfred\Desktop\inbox\{}.dxf"


def cleanup(dwg):
    pass


def main():
    for version in ("AC1015", "AC1018", "AC1021", "AC1024", "AC1027"):
        dwg = ezdxf.readfile(PATH.format(version))
        cleanup(dwg)
        dwg.save()

if __name__ == '__main__':
    main()