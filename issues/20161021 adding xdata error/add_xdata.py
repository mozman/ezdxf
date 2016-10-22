import ezdxf

dwg = ezdxf.new('AC1027')
dwg.appids.new('PE_URL')  # create APP ID entry
ms = dwg.modelspace()

c = ms.add_circle((10, 10), 100)
c.tags.new_xdata('PE_URL',
                 [
                     (1000, 'tralivali.ru'),
                     (1002, '{'),
                     (1000, 'tralivali'),
                     (1002, '{'),
                     (1071, 1),
                     (1002, '}'),
                     (1002, '}')
                 ])
dwg.saveas('xdata.dxf')

## Error message:
## Premature end of object
## invalid or incomplete DXF input -- drawing discarded.
## Press ENTER to continue