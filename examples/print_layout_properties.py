# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
import sys
import ezdxf


def print_layout(layout):
    dxf = layout.dxf_layout.dxf
    print("#LAYOUT: {}".format(layout.name))
    print("##PLOT SETTINGS:")
    print("(1) page_setup_name: {}  ".format(dxf.plot_configuration_file))
    print("(2) plot_configuration_file: {}  ".format(dxf.plot_configuration_file))
    print("(4) paper_size: {}  ".format(dxf.paper_size))
    print("(6) plot_view_name: {}  ".format(dxf.plot_view_name))
    print("(40) left_margin: {}  ".format(dxf.left_margin))
    print("(41) bottom_margin: {}  ".format(dxf.bottom_margin))
    print("(42) right_margin: {}  ".format(dxf.right_margin))
    print("(43) top_margin: {}  ".format(dxf.top_margin))
    print("(44) paper_width: {}  ".format(dxf.paper_width))
    print("(45) paper_height: {}  ".format(dxf.paper_height))
    print("(46) plot_origin_x_offset: {}  ".format(dxf.plot_origin_x_offset))
    print("(47) plot_origin_y_offset: {}  ".format(dxf.plot_origin_y_offset))
    print("(48) plot_window_x1: {}  ".format(dxf.plot_window_x1))
    print("(49) plot_window_y1: {}  ".format(dxf.plot_window_y1))
    print("(140) plot_window_x2: {}  ".format(dxf.plot_window_x2))
    print("(141) plot_window_y2: {}  ".format(dxf.plot_window_y2))
    print("(142) scale_numerator: {}  ".format(dxf.scale_numerator))
    print("(143) scale_denominator: {}  ".format(dxf.scale_denominator))
    print("(70) plot_layout_flags: {0} b{0:b}  ".format(dxf.plot_layout_flags))
    print("(72) plot_paper_units: {}  ".format(dxf.plot_paper_units))
    print("(73) plot_rotation: {}  ".format(dxf.plot_rotation))
    print("(74) plot_type: {}  ".format(dxf.plot_type))
    print("(7) current_style_sheet: {}  ".format(dxf.current_style_sheet))
    print("(75) standard_scale_type: {}  ".format(dxf.standard_scale_type))
    print("(147) unit_factor: {}  ".format(dxf.unit_factor))
    print("(148) paper_image_origin_x: {}  ".format(dxf.paper_image_origin_x))
    print("(149) paper_image_origin_y: {}  ".format(dxf.paper_image_origin_y))
    print("##LAYOUT SETTINGS:")
    print("(1) name: {}  ".format(dxf.name))
    print("(7) layout_flags: {}  ".format(dxf.name))
    print("(70) layout_flags: {0} b{0:b}  ".format(dxf.layout_flags))
    print("(71) taborder: {}  ".format(dxf.taborder))
    print("(10) limmin: {}  ".format(dxf.limmin))
    print("(11) limmax: {}  ".format(dxf.limmax))
    print("(12) insert_base: {}  ".format(dxf.insert_base))
    print("(14) extmin: {}  ".format(dxf.extmin))
    print("(15) extmax: {}  ".format(dxf.extmax))
    print("(146) elevation: {}  ".format(dxf.elevation))
    print("(13) ucs_origin: {}  ".format(dxf.ucs_origin))
    print("(16) ucs_xaxis: {}  ".format(dxf.ucs_xaxis))
    print("(17) ucs_yaxis: {}  ".format(dxf.ucs_yaxis))
    print("(76) ucs_type: {}\n".format(dxf.ucs_type))


def print_layouts(layouts):
    for layout in layouts:
        print_layout(layout)


def process_file(filename):
    doc = ezdxf.readfile(filename)
    if doc.dxfversion > 'AC1009':
        print_layouts(doc.layouts)
    else:
        print("DXF R12 not supported: {}".format(filename))


def run(files):
    for filename in files:
        process_file(filename)


if __name__ == '__main__':
    run(sys.argv[1:])
