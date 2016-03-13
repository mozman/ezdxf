import ezdxf

dwg = ezdxf.new('AC1015')  # image requires the DXF 2000 or newer format
my_image_def = dwg.add_image_def(key='mycat', filename=r'mycat.jpg', size_in_pixel=(640, 360))
msp = dwg.modelspace()
mesh = msp.add_image(insert=(10, 20), size_in_units=(6.4, 3.6), image_def=my_image_def, rotation=90)

# get existing image definitions
image_defs = dwg.objects.query('IMAGEDEF')  # get all image defs in drawing
# The IMAGEDEF entity is like a block definition, it just defines the image

# get existing images
images = dwg.entities.query('IMAGE')
# The IMAGE entity is like the INSERT entity, it creates an image reference,
# and there can be multiple references of the same picture in a drawing.

mykey = 'mycat'
while True:
    try:
        another_image_def = dwg.add_image_def(key=mykey, filename=r'mycat.jpg', size_in_pixel=(640, 360))
    except KeyError:
        mykey += '0'  # just try another key
    else:
        break


dwg.saveas("using_image.dxf")
