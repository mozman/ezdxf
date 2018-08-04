.. module:: ezdxf.algebra

This class located in module :mod:`ezdxf.algebra`::

    from ezdxf.algebra import Arc


Arc
---

.. class:: Arc

    This is a helper class to create parameters for the DXF :class:`Arc` class.


.. attribute:: Arc.center

    Center point as :class:`~ezdxf.algebra.Vector`

.. attribute:: Arc.radius

    Arc radius

.. attribute:: Arc.start_angle

    Start angle of arc in degrees.

.. attribute:: Arc.start_angle_rad

    Start angle of arc in radians.

.. attribute:: Arc.end_angle

    End angle of arc in degrees.

.. attribute:: Arc.end_angle_rad

    End angle of arc in radians.


Static Arc Methods
~~~~~~~~~~~~~~~~~~

.. method:: Arc.from_2p_angle(start_point, end_point, angle)

    Create arc from two points and enclosing angle. Additional precondition: arc goes in counter clockwise
    orientation from start_point to end_point. Z-axis of start_point and end_point has to be 0 if given.


    :param start_point: start point as (x, y [,z]) tuple
    :param end_point: end point as (x, y [,z]) tuple
    :param angle: enclosing angle in degrees

    :Return: new :class:`~ezdxf.algebra.Arc`

.. method:: Arc.from_3p(start_point, end_point, def_point)

    Create arc from three points. Additional precondition: arc goes in counter clockwise
    orientation from start_point to end_point. Z-axis of start_point, end_point and def_point has to be 0 if given.

    :param start_point: start point as (x, y [,z]) tuple
    :param end_point: end point as (x, y [,z]) tuple
    :param def_point: additional definition point as (x, y [,z]) tuple

    :Return: new :class:`~ezdxf.algebra.Arc`


