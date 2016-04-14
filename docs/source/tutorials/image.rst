.. _tut_image:

Tutorial for Image and ImageDef
===============================

Insert a raster image into a DXF drawing, the raster image is NOT embedded into the DXF file::

    import ezdxf


    dwg = ezdxf.new('AC1015')  # image requires the DXF R2000 format or later
    my_image_def = dwg.add_image_def(filename='mycat.jpg', size_in_pixel=(640, 360))
    # The IMAGEDEF entity is like a block definition, it just defines the image

    msp = dwg.modelspace()
    # add first image
    msp.add_image(insert=(2, 1), size_in_units=(6.4, 3.6), image_def=my_image_def, rotation=0)
    # The IMAGE entity is like the INSERT entity, it creates an image reference,
    # and there can be multiple references to the same picture in a drawing.

    msp.add_image(insert=(4, 5), size_in_units=(3.2, 1.8), image_def=my_image_def, rotation=30)

    # get existing image definitions, Important: IMAGEDEFs resides in the objects section
    image_defs = dwg.objects.query('IMAGEDEF')  # get all image defs in drawing

    dwg.saveas("dxf_with_cat.dxf")

