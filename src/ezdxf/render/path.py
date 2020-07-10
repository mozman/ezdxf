# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-07-10
"""
Path
====

This module implement a geometrical :class:`Path` supported by several render backends,
with the goal to create such paths from LWPOLYLINE, 2D POLYLINE and HATCH boundary paths
and send them to the render backend, see :mod:`ezdxf.addons.drawing`.

Minimum common interface:

- matplotlib: `PathPatch`_
    - matplotlib.path.Path() codes: 
    - MOVETO
    - LINETO
    - CURVE3 - quadratic bezier curve
    - CURVE4 - cubic bezier curve
    
- PyQt: `QPainterPath`_
    - moveTo()
    - lineTo()
    - quadTo() - quadratic bezier curve
    - cubicTo() - cubic bezier curve

- SVG: `SVG-Path`_
    - "M" - absolute move to
    - "L" - absolute line to
    - "Q" - absolute quadratic bezier curve
    - "C" - absolute cubic bezier curve


.. _PathPatch: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.PathPatch.html#matplotlib.patches.PathPatch
.. _QPainterPath: https://doc.qt.io/qtforpython/PySide2/QtGui/QPainterPath.html
.. _SVG-Path: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths

"""

