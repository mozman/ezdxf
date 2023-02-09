.. _mtxpl_addon:

MTextExplode
============

This tool is meant to explode MTEXT entities into single line TEXT entities by
replicating the MTEXT layout as close as possible. This tool requires the
optional Matplotlib package to create usable results, nonetheless it also
works without Matplotlib, but then uses a mono-spaced replacement font for
text size measuring which leads to very inaccurate results.

The supported MTEXT features are:

-  changing text color
-  text strokes: underline, overline and strike through
-  changing text size, width and oblique
-  changing font faces
-  stacked text (fractions)
-  multi-column support
-  background color
-  text frame

The tool requires an initialized DXF document io implement all these features
by creating additional text styles. When exploding multiple MTEXT entities,
they can share this new text styles. Call the :meth:`MTextExplode.finalize`
method just once after all MTEXT entities are processed to create the
required text styles, or use :class:`MTextExplode` as context manager by
using the ``with`` statement, see examples below.

There are also many limitations:

-  A 100% accurate result cannot be achieved.
-  Character tracking is not supported.
-  Tabulator stops have only limited support for LEFT and JUSTIFIED aligned
   paragraphs to support numbered and bullet lists. An excessive use of tabs
   will lead to incorrect results.
-  The DISTRIBUTED alignment will be replaced by the JUSTIFIED alignment.
-  Text flow is always "left to right".
-  The line spacing mostly corresponds to the "EXACT" style, except for
   stacked text (fractions), which corresponds more to the "AT LEAST" style,
   but not precisely. This behavior maybe will improve in the future.
-  FIELDS are not evaluated by *ezdxf*.

.. autoclass:: ezdxf.addons.MTextExplode(layout, doc=None, spacing_factor = 1.0)

    .. automethod:: explode

    .. automethod:: finalize

Example to explode all MTEXT entities in the DXF file "mtext.dxf":

.. code-block:: python

    import ezdxf
    from ezdxf.addons import MTextExplode

    doc = ezdxf.readfile("mtext.dxf")
    msp = doc.modelspace()
    with MTextExplode(msp) as xpl:
        for mtext in msp.query("MTEXT"):
            xpl.explode(mtext)
    doc.saveas("xpl_mtext.dxf")

Explode all MTEXT entities into the block "EXPLODE":

.. code-block:: python

    import ezdxf
    from ezdxf.addons import MTextExplode

    doc = ezdxf.readfile("mtext.dxf")
    msp = doc.modelspace()
    blk = doc.blocks.new("EXPLODE")
    with MTextExplode(blk) as xpl:
        for mtext in msp.query("MTEXT"):
            xpl.explode(mtext)
    msp.add_block_ref("EXPLODE", (0, 0))
    doc.saveas("xpl_into_block.dxf")
