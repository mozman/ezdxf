__author__ = 'manfred'

import ezdxf

PATH = r"C:\Users\manfred\Desktop\now\templates\{}.dxf"


def add_appids(dwg):
    if "HATCHBACKGROUNDCOLOR" not in dwg.appids:
        dwg.appids.new("HATCHBACKGROUNDCOLOR", {'flags': 0})


def repair_layer_pointers(dwg):
    # set valid plot style name handle in all layers
    plot_style_names = dwg.rootdict.get_entity('ACAD_PLOTSTYLENAME')
    normal_plot_style = plot_style_names.get_handle('Normal')
    for layer in dwg.layers:
        # remove 347 and 348(?) group code
        tags = layer.tags.get_subclass('AcDbLayerTableRecord')
        tags.remove_tags((348, 347))

        # set valid plot style name handle
        if layer.dxf.plot_style_name not in dwg.entitydb:
            layer.dxf.plot_style_name = normal_plot_style


def remove_all_text_styles(dwg):
    delete = []
    for style in dwg.styles:
        if style.dxf.name.upper() == 'STANDARD':
            style.dxf.font = 'txt'
        else:
            delete.append(style.dxf.name)
    for name in delete:
        dwg.styles.remove(name)


def remove_all_dim_styles(dwg):
    delete = [dimstyle.dxf.name for dimstyle in dwg.dimstyles if dimstyle.dxf.name.upper() != 'STANDARD']
    for name in delete:
        dwg.dimstyles.remove(name)


def remove_all_linetypes_styles(dwg):
    protect = {'bylayer', 'byblock', 'continuous'}
    delete = [ltype.dxf.name for ltype in dwg.linetypes if ltype.dxf.name.lower() not in protect]
    for name in delete:
        dwg.linetypes.remove(name)


def remove_layer_view_port(dwg):
    if 'VIEW_PORT' in dwg.layers:
            dwg.layers.remove('VIEW_PORT')
    if 'View Port' in dwg.layers:
            dwg.layers.remove('View Port')


def main():
    for version in ("AC1009", "AC1015", "AC1018", "AC1021", "AC1024", "AC1027", "AC1032"):
        dwg = ezdxf.readfile(PATH.format(version))
        dwg.save()


if __name__ == '__main__':
    main()
