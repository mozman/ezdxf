__author__ = 'manfred'

import ezdxf

PATH = r"C:\Users\manfred\Desktop\now\{}.dxf"


def add_appids(dwg):
    if "HATCHBACKGROUNDCOLOR" not in dwg.appids:
        dwg.appids.new("HATCHBACKGROUNDCOLOR", {'flags': 0})


def repair_layer_pointers(dwg):
    # set valid plot style name handle in all layers
    default_plot_style_name = dwg.rootdict.get_entity('ACAD_PLOTSTYLENAME')
    normal_plot_style = default_plot_style_name.get('Normal')
    for layer in dwg.layers:
        # remove 348 (?) group code
        tags = layer.tags.get_subclass('AcDbLayerTableRecord')
        tags.remove_tags((348, 347))

        # set valid plot style name handle
        if layer.dxf.plot_style_name not in dwg.entitydb:
            layer.dxf.plot_style_name = normal_plot_style


def main():
    for version in ("AC1015", "AC1018", "AC1021", "AC1024", "AC1027", "AC1032"):
        dwg = ezdxf.readfile(PATH.format(version))
        # add_appids(dwg)
        repair_layer_pointers(dwg)
        dwg.save()


if __name__ == '__main__':
    main()