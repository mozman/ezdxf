.. module:: ezdxf.addons.text2path

text2path
=========

.. versionadded:: 0.16

Tools to convert text strings and text based DXF entities into outer- and inner
linear paths as :class:`~ezdxf.path.Path` objects. These tools depend on
the optional `Matplotlib`_ package.

Text Alignments
---------------

The text alignments work the same way as for the :class:`~ezdxf.entities.Text`
entity:

============   =============== ================= =====
Vertical       Left            Center            Right
============   =============== ================= =====
Top            TOP_LEFT        TOP_CENTER        TOP_RIGHT
Middle         MIDDLE_LEFT     MIDDLE_CENTER     MIDDLE_RIGHT
Bottom         BOTTOM_LEFT     BOTTOM_CENTER     BOTTOM_RIGHT
Baseline       LEFT            CENTER            RIGHT
============   =============== ================= =====

The vertical middle alignments (MIDDLE_XXX), center the text
vertically in the middle of the uppercase letter "X" (cap height).

Special alignments, where the horizontal alignment is always in the center of
the text:

- ALIGNED: text is scaled to match the given `length`, scales x- and
  y-direction by the same factor.
- FIT: text is scaled to match the given `length`, but scales only in
  x-direction.
- MIDDLE: insertion point is the center of the total height (cap height +
  descender height) without scaling, the `length` argument is ignored.

Font Face Definition
--------------------

TODO require docs for ezdxf.tools.fonts

String Functions
----------------

.. autofunction:: make_paths_from_str(s: str, font: FontFace, size: float = 1.0, align: str = "LEFT", length: float = 0, m: Matrix44 = None) -> List[Path]

.. autofunction:: make_hatches_from_str(s: str, font: FontFace, size: float = 1.0,align: str = "LEFT", length: float = 0, segments: int = 4, dxfattribs: Dict = None m: Matrix44 = None) -> List[Hatch]

Entity Functions
----------------

.. autofunction:: make_paths_from_entity(entity)-> List[Path]

.. autofunction:: make_hatches_from_entity(entity) -> List[Hatch]

.. autofunction:: explode(entity, kind = 1, target = None) -> EntityQuery

Utility Functions
-----------------

.. autofunction:: group_contour_and_holes(Iterable[Path]) -> Iterable[Tuple[Path, List[Path]]]

.. _Matplotlib: https://matplotlib.org