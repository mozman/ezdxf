.. module:: ezdxf.addons.text2path

text2path
=========

.. versionadded:: 0.16

Tools to convert text strings and text based DXF entities into outer- and inner
linear paths as :class:`~ezdxf.render.path.Path` objects. These tools depend on
the optional `matplotlib`_ package.

.. warning::

    Conversion of TEXT entities into hatches does not work for spatial text not
    located in the xy-plane. Contour and hole detection is done in the xy-plane
    by 2D bounding boxes to be fast.

.. autofunction:: make_paths_from_str(s: str, font: FontFace, halign: int = 0, valign: int = 0, m: Matrix44 = None) -> List[Path]

.. autofunction:: make_hatches_from_str(s: str, font: FontFace, halign: int = 0, valign: int = 0, segments: int = 4, dxfattribs: Dict = None m: Matrix44 = None) -> List[Hatch]

.. autofunction:: make_paths_from_entity(entity)-> List[Path]

.. autofunction:: make_hatches_from_entity(entity) -> List[Hatch]

.. autofunction:: group_contour_and_holes(Iterable[Path]) -> Iterable[Tuple[Path, List[Path]]]

.. _matplotlib: https://matplotlib.org