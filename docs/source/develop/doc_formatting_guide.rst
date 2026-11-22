.. sphinx comments

Formatting Guide
================

This section is only for `myself <https://github.com/mozman>`_, because of the
long pauses between develop iterations, I often forget to be consistent in
documentation formatting.

Documentation is written with `Sphinx`_ and `reSturcturedText`_.

Started integration of documentation into source code and using `autodoc`_
features of `Sphinx`_ wherever useful.

.. inline link

Sphinx theme provided by `Read the Docs <https://readthedocs.org>`_ : ::

    pip install sphinx-rtd-theme


:mod:`guide` --- Example module
-------------------------------

.. module:: guide
    :synopsis: Example for documentation formatting

.. function:: example_func(a:int, b:str, test:str=None, flag:bool=True) -> None

    Parameters `a` and `b` are positional arguments, argument `test` defaults
    to ``None`` and `flag` to ``True``.
    Set `a` to 70 and `b` to "x" as an example. Inline code examples
    :code:`example_func(70, 'x')` or simple ``example_func(70, "x")``

        - arguments: `a`, `b`, `test` and `flags`
        - literal number values: 1, 2 ... 999
        - literal string values: "a String"
        - literal tags: (5, "F000")
        - inline code: call a :code:`example_func(x)`
        - Python keywords: ``None``, ``True``, ``False``, ``tuple``, ``list``, ``dict``, ``str``, ``int``, ``float``
        - Exception classes: :class:`DXFAttributeError`

.. class:: ExampleCls(**kwargs)

    The :class:`ExampleCls` constructor accepts a number of optional keyword
    arguments.  Each keyword argument corresponds to an instance attribute, so
    for example ::

        e = ExampleCls(flag=True)


    .. attribute:: flag

        This is the attribute :attr:`flag`.

    .. method:: set_axis(axis)

        axis as (x, y, z) tuple

        Args:
            axis: (x, y, z) tuple

    .. method:: example_method(flag:bool=False)->None

        Method :meth:`example_method` of class :class:`ExampleCls`

Language Style
--------------

New text in docstrings and documentation pages uses Simplified Technical
English (STE100) in spirit, not strictly. Existing text is migrated step by
step - do not restyle a page while working on something else.

- Active voice and simple present tense, imperative for instructions. Passive
  voice is acceptable when the actor is unknown or irrelevant: "a `DXFError` is
  raised".
- One idea per sentence, 20 words in procedures and 25 words in descriptions.
- One topic per paragraph, six sentences at most.
- ``must`` for requirements, ``can`` for permission, possibility or failure.
  Remove ``should``, ``may``, ``might``, ``could`` and ``would`` unless the
  sentence loses accuracy.
- One term for one concept. Use the terms from "Text Formatting" below and the
  names that the API uses, and qualify an ambiguous word: "Python attribute"
  vs. "DXF ATTRIB entity".
- No contractions, slang, idioms or humor, and no filler words like "simply",
  "just" or "obviously".
- Use a vertical list for three or more parallel items or steps.
- Identifiers, DXF names and type names are not dictionary words. These rules
  never override accuracy or Sphinx markup.

AI agents get the same rules in ``AGENTS.md``.

Text Formatting
---------------

DXF version
    DXF R12 (AC1009), DXF R2004 (AC1018)

DXF Types
    DXF types are always written in uppercase letters but without further formatting: DXF, LINE, CIRCLE

(internal API)
    Marks methods as internal API, gets no public documentation.

(internal class)
    Marks classes only for internal usage, gets not public documentation.

Spatial Dimensions
    2D and 3D with an uppercase letter D

Axis
    x-axis, y-axis and z-axis

Planes
    xy-plane, xz-plane, yz-plane

Layouts
    modelspace, paperspace [layout], block [layout]

Extended Entity Data
    AppData, XDATA, embedded object, APPID

.. _Sphinx: http://www.sphinx-doc.org/en/master/
.. _autodoc: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
.. _reSturcturedText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html