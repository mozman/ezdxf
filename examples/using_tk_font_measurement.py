import ezdxf


TTF = "LiberationSansNarrow-Regular.ttf"  # the real file system name of the ttf file
STYLE_NAME = "LIBERATION_SANS_NARROW"  # name as stored in the DXF Style Table

dwg = ezdxf.new('R12')
# here the real file system name of the ttf file is needed, maybe system_font_name works too
liberation_font = dwg.styles.new(STYLE_NAME, {'font': TTF})

msp = dwg.modelspace()
text = "This is a Test!"
text_entity = msp.add_text(text, {'height': 2.5, 'style': STYLE_NAME}).set_pos((0, 0))

fm = liberation_font.tk_font_tool()
length = fm.text_width(text_entity)
msp.add_line((0, 0), (length, 0), {'color': 2})


dwg.saveas('using_tk_font_measurement.dxf')
