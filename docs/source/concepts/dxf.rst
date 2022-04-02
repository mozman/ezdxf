.. _what is dxf:

What is DXF?
============

The common assumption is also the cite of `Wikipedia`_:

    AutoCAD DXF (Drawing eXchange Format) is a CAD data file format developed by
    Autodesk for enabling data interoperability between AutoCAD and **other**
    applications.

    DXF was originally introduced in December 1982 as part of AutoCAD 1.0, and was
    intended to provide an exact representation of the data in the AutoCAD native
    file format, DWG (Drawing). For many years Autodesk did not publish
    specifications making correct imports of DXF files difficult. Autodesk now
    publishes the DXF specifications online.

The more precise cite from the `DXF reference`_ itself:

    The DXF™ format is a tagged data representation of all the information contained
    in an AutoCAD® drawing file. Tagged data means that each data element in the
    file is preceded by an integer number that is called a group code. A group
    code's value indicates what type of data element follows. This value also
    indicates the meaning of a data element for a given object (or record) type.
    Virtually all user-specified information in a drawing file can be represented
    in DXF format.

No mention of interoperability between AutoCAD and **other** applications.

In reality the DXF format was designed to ensure AutoCAD cross-platform
compatibility in the early days when different hardware platforms with different
binary data formats were used. The name DXF (Drawing eXchange Format) may
suggest an universal exchange format, but it is not. It is based on the
infrastructure installed by Autodesk products (fonts) and the implementation
details of AutoCAD (MTEXT) or on licensed third party technologies
(embedded ACIS entities).

For more information about the AutoCAD history see the document:
`The Autodesk File`_ - Bits of History, Words of Experience by *John Walker*,
founder of *Autodesk, Inc.* and co-author of *AutoCAD*.

DXF Reference Quality
---------------------

The `DXF reference`_ is by far no specification nor a standard like the
W3C standard for `SVG`_ or the ISO standard for `PDF`_.

The reference describes many but not all DXF entities and some basic concepts
like the tag structure or the arbitrary axis algorithm.
But the existing documentation (reference) is incomplete and partly misleading
or wrong. Also missing from the reference are some important parts like the complex
relationship between the entities to create higher order structures like block
definitions, layouts (model space & paper space) or dynamic blocks to name a few.

Reliable CAD Applications
-------------------------

Because of the suboptimal quality of the DXF reference not all DXF viewers,
creators or processors are of equal quality. I consider a CAD application
as a :term:`reliable CAD application` when the application creates valid DXF
documents in the meaning and interpretation of `Autodesk`_ and a reliable DXF
viewer when the result matches in most parts the result of the free `Trueview`_
viewer provided by `Autodesk`_.

These are some applications which do fit the criteria of a reliable CAD application:

- `AutoCAD`_ and `Trueview`_
- CAD applications based on the `OpenDesignAlliance`_ (ODA) SDK, see also
  `ODA on wikipedia`_, even `Autodesk`_ is a corporate member, see their blog post
  from `22 Sep 2020 <https://adsknews.autodesk.com/news/open-design-alliance-membership>`_
  at `adsknews`_ but only to use the ODA IFC tools and not to improve the DWG/DXF
  compatibility
- `BricsCAD`_ (ODA based)
- `GstarCAD`_ (ODA based)
- `ZWCAD`_ (ODA based)


Unfortunately, I cannot recommend any open source applications because everyone
I know has serious shortcomings, at least as a DXF viewer, and I don't trust
them as a DXF creator either. To be clear, not even `ezdxf` (which is not a CAD
application) is a `reliable` library in this sense - it just keeps getting better,
but is far from `reliable`.

BTW: Don't send bug reports based on `LibreCAD`_ or `QCAD`_, I won't waste my
time on them.

.. _Wikipedia: https://en.wikipedia.org/wiki/AutoCAD_DXF

.. _DXF reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3

.. _The Autodesk file: https://www.fourmilab.ch/autofile/

.. _SVG: https://www.w3.org/Graphics/SVG/

.. _PDF: https://en.wikipedia.org/wiki/PDF

.. _Autodesk: https://www.autodesk.com/

.. _Trueview: https://www.autodesk.com/viewers

.. _AutoCAD: https://www.autodesk.com/products/autocad/overview

.. _BricsCAD: https://www.bricsys.com/en-intl/

.. _GstarCAD: https://www.gstarcad.net/

.. _ZWCAD: https://www.zwsoft.com/product/zwcad

.. _OpenDesignAlliance: https://www.opendesign.com/

.. _ODA on Wikipedia: https://en.wikipedia.org/wiki/Open_Design_Alliance

.. _LibreCAD: https://librecad.org/

.. _QCAD: https://qcad.org/en/

.. _adsknews: https://adsknews.autodesk.com/