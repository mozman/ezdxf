# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
import os
import shutil

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds an image to the DXF file.
#
# My advice: Do not use pixel images in DXF files!
# docs: https://ezdxf.mozman.at/docs/dxfentities/ellipse.html
# ------------------------------------------------------------------------------

IMAGE_PATH = "mycat.jpg"
ABS_IMAGE_PATH = os.path.abspath(IMAGE_PATH)

# The IMAGE entity requires the DXF R2000 or newer format:
doc = ezdxf.new("R2004")
my_image_def = doc.add_image_def(
    filename=ABS_IMAGE_PATH, size_in_pixel=(640, 360)
)
# image definition is like a block definition

msp = doc.modelspace()
# add first image, image is like a block reference (INSERT)
msp.add_image(
    image_def=my_image_def, insert=(2, 1), size_in_units=(6.4, 3.6), rotation=0
)

# add first image
msp.add_image(
    image_def=my_image_def, insert=(4, 5), size_in_units=(3.2, 1.8), rotation=30
)

# rectangular boundaries
image = msp.add_image(
    image_def=my_image_def, insert=(10, 1), size_in_units=(6.4, 3.6), rotation=0
)
image.set_boundary_path([(50, 50), (600, 300)])

# user defined boundary path
image = msp.add_image(
    image_def=my_image_def, insert=(10, 5), size_in_units=(6.4, 3.6), rotation=0
)
image.set_boundary_path([(50, 50), (500, 70), (450, 300), (70, 280)])

# get existing image definitions
image_defs = doc.objects.query("IMAGEDEF")  # get all image defs in drawing
# The IMAGEDEF entity is like a block definition, it just defines the image

# get existing images
images = msp.query("IMAGE")
# The IMAGE entity is like the INSERT entity, it creates an image reference,
# and there can be multiple references of the same picture in a drawing.


doc.saveas(CWD / "image_abs.dxf")

# The IMAGE reference by absolute path works best, but it's a problem if you
# want to distribute your DXF files.
# IMPORTANT: This does NOT work with Autodesk products like DWG TrueView or AutoCAD!

my_image_def.dxf.filename = IMAGE_PATH
doc.saveas(CWD / "image_rel.dxf")

# copy the image file to the same folder as the DXF document
shutil.copy(IMAGE_PATH, CWD / IMAGE_PATH)

# The relative path works with BricsCAD but not with AutoCAD.

# ------------------------------------------------------------------------------
# My advice: Do not use pixel images in DXF files!
# ------------------------------------------------------------------------------
