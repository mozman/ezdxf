# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import sys
import ezdxf

# ------------------------------------------------------------------------------
# print DXF attributes of layouts
#
# docs about layouts: https://ezdxf.mozman.at/docs/layouts/index.html
# ------------------------------------------------------------------------------


def print_layout(layout):
    dxf = layout.dxf_layout.dxf
    print(f"#LAYOUT: {layout.name}")
    print("##PLOT SETTINGS:")
    print(f"(1) page_setup_name: {dxf.plot_configuration_file}")
    print(f"(2) plot_configuration_file: {dxf.plot_configuration_file}")
    print(f"(4) paper_size: {dxf.paper_size}")
    print(f"(6) plot_view_name: {dxf.plot_view_name}")
    print(f"(40) left_margin: {dxf.left_margin}")
    print(f"(41) bottom_margin: {dxf.bottom_margin}")
    print(f"(42) right_margin: {dxf.right_margin}")
    print(f"(43) top_margin: {dxf.top_margin}")
    print(f"(44) paper_width: {dxf.paper_width}")
    print(f"(45) paper_height: {dxf.paper_height}")
    print(f"(46) plot_origin_x_offset: {dxf.plot_origin_x_offset}  ")
    print(f"(47) plot_origin_y_offset: {dxf.plot_origin_y_offset}  ")
    print(f"(48) plot_window_x1: {dxf.plot_window_x1}")
    print(f"(49) plot_window_y1: {dxf.plot_window_y1}")
    print(f"(140) plot_window_x2: {dxf.plot_window_x2}")
    print(f"(141) plot_window_y2: {dxf.plot_window_y2}")
    print(f"(142) scale_numerator: {dxf.scale_numerator}")
    print(f"(143) scale_denominator: {dxf.scale_denominator}")
    flags = dxf.plot_layout_flags
    print(f"(70) plot_layout_flags: {flags} b{flags:b}")
    print(f"(72) plot_paper_units: {dxf.plot_paper_units}")
    print(f"(73) plot_rotation: {dxf.plot_rotation}")
    print(f"(74) plot_type: {dxf.plot_type}")
    print(f"(7) current_style_sheet: {dxf.current_style_sheet}")
    print(f"(75) standard_scale_type: {dxf.standard_scale_type}")
    print(f"(147) unit_factor: {dxf.unit_factor}")
    print(f"(148) paper_image_origin_x: {dxf.paper_image_origin_x}")
    print(f"(149) paper_image_origin_y: {dxf.paper_image_origin_y}")
    print("##LAYOUT SETTINGS:")
    print(f"(1) name: {dxf.name}  ")
    print(f"(7) layout_flags: {dxf.name}  ")
    flags = dxf.layout_flags
    print(f"(70) layout_flags: {flags} b{flags:b}")
    print(f"(71) taborder: {dxf.taborder}")
    print(f"(10) limmin: {dxf.limmin}")
    print(f"(11) limmax: {dxf.limmax}  ")
    print(f"(12) insert_base: {dxf.insert_base}")
    print(f"(14) extmin: {dxf.extmin}")
    print(f"(15) extmax: {dxf.extmax}")
    print(f"(146) elevation: {dxf.elevation}")
    print(f"(13) ucs_origin: {dxf.ucs_origin}")
    print(f"(16) ucs_xaxis: {dxf.ucs_xaxis}")
    print(f"(17) ucs_yaxis: {dxf.ucs_yaxis}")
    print(f"(76) ucs_type: {dxf.ucs_type}\n")


def print_layouts(layouts):
    for layout in layouts:
        print_layout(layout)


def process_file(filename):
    doc = ezdxf.readfile(filename)
    if doc.dxfversion > "AC1009":
        print_layouts(doc.layouts)
    else:
        print(f"DXF R12 not supported: {filename}")


def run(files):
    for filename in files:
        process_file(filename)


if __name__ == "__main__":
    run(sys.argv[1:])
