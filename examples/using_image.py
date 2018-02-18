# Copyright (c) 2016 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf

dwg = ezdxf.new('R2004')  # image requires the DXF 2000 or newer format
my_image_def = dwg.add_image_def(filename='mycat.jpg', size_in_pixel=(640, 360))
# image definition is like a block definition

msp = dwg.modelspace()
# add first image, image is like a block reference (INSERT)
msp.add_image(image_def=my_image_def, insert=(2, 1), size_in_units=(6.4, 3.6), rotation=0)
# add first image
msp.add_image(image_def=my_image_def, insert=(4, 5), size_in_units=(3.2, 1.8), rotation=30)

# get existing image definitions
image_defs = dwg.objects.query('IMAGEDEF')  # get all image defs in drawing
# The IMAGEDEF entity is like a block definition, it just defines the image

# get existing images
images = dwg.entities.query('IMAGE')
# The IMAGE entity is like the INSERT entity, it creates an image reference,
# and there can be multiple references of the same picture in a drawing.


dwg.saveas("using_image.dxf")
