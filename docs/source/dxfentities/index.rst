DXF Entities
============

.. module:: ezdxf.entities

All DXF entities can only reside in the :class:`~ezdxf.layouts.BaseLayout`
and inherited classes like :class:`~ezdxf.layouts.Modelspace`,
:class:`~ezdxf.layouts.Paperspace` and :class:`~ezdxf.layouts.BlockLayout`.

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. toctree::
    :maxdepth: 1

    dxfentity
    dxfgfx
    3dface
    3dsolid
    arc
    ../blocks/attrib
    body
    circle
    dimension
    arcdim
    ellipse
    hatch
    helix
    image
    ../blocks/insert
    leader
    line
    lwpolyline
    mline
    mesh
    mpolygon
    mtext
    mleader
    point
    polyline
    ray
    region
    shape
    solid
    spline
    surface
    text
    trace
    underlay
    viewport
    wipeout
    xline