.. module:: ezdxf.render.revcloud

Revision Cloud
==============


..  autofunction:: points


Usage:

.. code-block::


    import ezdxf
    from ezdxf.render import revcloud

    doc = ezdxf.new()
    msp = doc.modelspace()
    lw_points = revcloud.points(
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        segment_length=0.1,
        bulge=0.5,
        start_width=0.01,
        end_width=0,
    )
    msp.add_lwpolyline(lw_points)
    doc.saveas("revcloud.dxf")

.. figure:: gfx/revcloud.png

