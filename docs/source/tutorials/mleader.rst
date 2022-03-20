.. _tut_mleader:

Tutorial for MultiLeader
========================

.. versionadded:: 0.18

A multileader object typically consists of an arrowhead, a horizontal landing
(a.k.a. "dogleg"), a leader line or curve, and either a MTEXT object or a BLOCK.

Because of the complexity of the MULTILEADER entity, the factory method
:meth:`~ezdxf.layouts.BaseLayout.add_multileader_mtext` returns a
:class:`~ezdxf.render.MultiLeaderMTextBuilder` instance to build a new entity
and the factory method :meth:`~ezdxf.layouts.BaseLayout.add_multileader_block`
returns a :class:`~ezdxf.render.MultiLeaderBlockBuilder` instance.

Due of the lack of good documentation it's not possible to support all
combinations of MULTILEADER properties with decent quality, so stick to recipes
and hints shown in this tutorial to get usable results otherwise, you will enter
uncharted territory.

The rendering result of the MULTILEADER entity is highly dependent on the CAD
application. The MULTILEADER entity does not have a pre-rendered anonymous
block of DXF primitives like the DIMENSION entities, so results may vary
from CAD application to CAD application.

.. seealso::

    - :class:`ezdxf.render.MultiLeaderBuilder` classes
    - :class:`ezdxf.entities.MultiLeader` class
    - :class:`ezdxf.entities.MLeaderStyle` class
    - :class:`ezdxf.tools.text.MTextEditor` class
    - :ref:`mleader internals`

MTEXT Quick Draw
----------------

Full Python script: `mtext_quick_leader.py`_

The :meth:`quick_leader()` method of a MTEXT - MULTILEADER entity constructs the
geometry parameters in reverse manner, starting from a given target point:

DXF document setup:

.. literalinclude:: src/mleader/mtext_quick_leader.py
    :lines: 18-23

Draw a red circle to mark the target point:

.. literalinclude:: src/mleader/mtext_quick_leader.py
    :lines: 24-27

Create four MULTILEADER entities pointing at the target point, the first segment
of the leader line is determined by an angle in this example pointing away from
the target point:

.. literalinclude:: src/mleader/mtext_quick_leader.py
    :lines: 29-35

.. image:: gfx/mleader_mtext_quick_leader_0.png

.. _mtext_quick_leader.py: https://github.com/mozman/ezdxf/blob/master/docs/source/tutorials/src/mleader/mtext_quick_leader.py

The content is automatically aligned to the end of the leader line. The first
segment is a relative vector to the target point and the optional second segment
vector is relative to the end of the first segment.
The default connection type is horizontal but can be changed to vertical.
This method is not very customizable for ease of use, but follows the settings
of the associated :class:`~ezdxf.entities.MLeaderStyle`.

The following sections show how to have more control when adding MULTILEADER
entities.

Create MTEXT Content
--------------------

TODO

MTEXT Connection Types
~~~~~~~~~~~~~~~~~~~~~~

TODO

MTEXT Alignment
~~~~~~~~~~~~~~~

TODO

Create BLOCK Content
--------------------

TODO

BLOCK Connection Types
~~~~~~~~~~~~~~~~~~~~~~

TODO

BLOCK Alignment
~~~~~~~~~~~~~~~

TODO

BLOCK Scaling
~~~~~~~~~~~~~

TODO

BLOCK Attributes
~~~~~~~~~~~~~~~~

TODO

Leader Properties
-----------------

TODO

Connection Properties
~~~~~~~~~~~~~~~~~~~~~

TODO

Polyline Leader
~~~~~~~~~~~~~~~

TODO

Spline Leader
~~~~~~~~~~~~~

TODO

Line Styling
~~~~~~~~~~~~

TODO

Arrowheads
~~~~~~~~~~

TODO

Overall Scaling
---------------

TODO

Setup MLEADERSTYLE
------------------

TODO