.. _faq:

FAQ
===

These are the old FAQ until late 2023, new FAQs will only be added to the 
:ref:`Knowledge_Graph`.

.. _faq001:

What is the Relationship between ezdxf, dxfwrite and dxfgrabber?
----------------------------------------------------------------

In 2010 I started my first Python package for creating DXF documents called `dxfwrite`,
this package can't read DXF files and writes only the DXF R12 (AC1009) version.
While `dxfwrite` works fine, I wanted a more versatile package, that can read
and write DXF files and maybe also supports newer DXF formats than DXF R12.

This was the start of the `ezdxf` package in 2011, but the progress was so slow,
that I created a spin off in 2012 called `dxfgrabber`, which implements only the
reading part of `ezdxf`, which I needed for my work and I wasn't sure if `ezdxf`
will ever be usable. Luckily in 2014 the first usable version of `ezdxf` could
be released. The `ezdxf` package has all the features of `dxfwrite` and
`dxfgrabber` and much more, but with a different API. So `ezdxf` is not a
drop-in replacement for `dxfgrabber` or `dxfwrite`.

Since `ezdxf` can do all the things that `dxfwrite` and `dxfgrabber` can do, I
focused on the development of `ezdxf`, `dxfwrite` and `dxfgrabber` are in
maintenance-only mode and will not get any new features, just bugfixes.

There are no advantages of `dxfwrite` over `ezdxf`, `dxfwrite` has a smaller
memory footprint, but the :mod:`r12writer` add-on does the same job as
`dxfwrite` without any in-memory structures by writing direct to a stream
or file and there is also no advantage of `dxfgrabber` over `ezdxf` for ordinary
DXF files, the smaller memory footprint of `dxfgrabber` is not noticeable and
for really big files the :mod:`iterdxf` add-on does a better job.

.. _faq002:

Imported ezdxf package has no content. (readfile, new)
------------------------------------------------------

1. AttributeError: partially initialized module 'ezdxf' has no attribute 'readfile'
   (most likely due to a circular import)

   Did you name your file/script "ezdxf.py"? This causes problems with
   circular imports. Renaming your file/script should solve this issue.

2. AttributeError: module 'ezdxf' has no attribute 'readfile'

   This could be a hidden permission error, for more information about this issue
   read Petr Zemeks article: https://blog.petrzemek.net/2020/11/17/when-you-import-a-python-package-and-it-is-empty/

.. _faq003:

How to add/edit ACIS based entities like 3DSOLID, REGION or SURFACE?
--------------------------------------------------------------------

The BODY, 3DSOLID, SURFACE, REGION and so on, are stored as ACIS data embedded
in the DXF file. The ACIS data is stored as SAT (text) format in the entity
itself for DXF R2000-R2010 and as SAB (binary) format in the
ACDSDATA section for DXF R2013+. `Ezdxf` can read SAT and SAB data, but
only write SAT data.

The ACIS data is a proprietary format from `Spatial Inc.`_, and there exist no
free available documentation or open source libraries to create or edit SAT or
SAB data, and also `ezdxf` provides no functionality for creating or editing
ACIS data.

The ACIS support provided by `ezdxf` is only useful for users which have
access to the ACIS SDK from `Spatial Inc.`_.

.. _Spatial Inc.: https://www.spatial.com/products/3d-acis-modeling

.. _faq004:

Are OLE/OLE2 entities supported?
--------------------------------

TLDR; NO!

The Wikipedia definition of `OLE`_: Object Linking & Embedding (OLE) is a proprietary
technology developed by Microsoft that allows embedding and linking to documents
and other objects. For developers, it brought OLE Control Extension (OCX), a
way to develop and use custom user interface elements. On a technical level, an
OLE object is any object that implements the ``IOleObject`` interface, possibly
along with a wide range of other interfaces, depending on the object's needs.

Therefore `ezdxf` does not support this entities in any way, this only
work on Windows and with the required editing application installed.
The binary data stored in the OLE objects cannot be used without the
editing application.

In my opinion, using OLE objects in a CAD drawing is a very bad design decision
that can and will cause problems opening these files in the future, even in
AutoCAD on Windows when the required editing application is no longer available
or the underlying technology is no longer supported.

All of this is unacceptable for a data storage format that should be accessed
for many years or decades (e.g. construction drawings for buildings or bridges).

Rendering SHX fonts
-------------------

The SHX font format is not documented nor supported by many libraries/packages
like `Matplotlib` and `Qt`, therefore only SHX fonts which have corresponding
TTF-fonts can be rendered by these backends. See also how-tos about
:ref:`howto_fonts`

Drawing Add-on
--------------

There is a dedicated how-to section for the :ref:`how_to_drawing_addon`.

Is the AutoCAD command XYZ available?
-------------------------------------

TLDR; Would you expect Photoshop features from a JPG library?

The package is designed as an interface to the DXF format and therefore does not offer
any advanced features of interactive CAD applications. First, some tasks are difficult
to perform without human guidance, and second, in complex situations, it's not that easy
to tell a "headless" system what exactly to do, so it's very likely that not many users
would ever use these features, despite the fact that a lot of time and effort would have
to be spent on development, testing and long-term support.

.. _OLE: https://en.wikipedia.org/wiki/Object_Linking_and_Embedding