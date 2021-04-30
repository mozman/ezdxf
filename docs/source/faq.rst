.. _faq:

FAQ
===

.. _faq001:

What is the Relationship between ezdxf, dxfwrite and dxfgrabber?
----------------------------------------------------------------

In 2010 I started my first Python package for creating DXF documents called `dxfwrite`, this package can't
read DXF files and writes only the DXF R12 (AC1009) version. While `dxfwrite` works fine, I wanted a more
versatile package, that can read and write DXF files and maybe also supports newer DXF formats than DXF R12.

This was the start of the `ezdxf` package in 2011, but the progress was so slow, that I created a spin off
in 2012 called `dxfgrabber`, which implements only the reading part of `ezdxf`, which I needed for my work
and I wasn't sure if `ezdxf` will ever be usable. Luckily in 2014 the first usable version of `ezdxf` could
be released. The `ezdxf` package has all the features of `dxfwrite` and `dxfgrabber` and much more, but with
a different API. So `ezdxf` is not a drop-in replacement for `dxfgrabber` or `dxfwrite`.

Since `ezdxf` can do all the things that `dxfwrite` and `dxfgrabber` can do, I focused on the development of
`ezdxf`, `dxfwrite` and `dxfgrabber` are in maintenance mode only and will not get any new features, just bugfixes.

There are no advantages of `dxfwrite` over `ezdxf`, `dxfwrite` has the smaller memory footprint, but the
:mod:`r12writer` add-on does the same job as `dxfwrite` without any in memory structures by writing direct to a stream
or file and there is also no advantage of `dxfgrabber` over `ezdxf` for normal DXF files the smaller memory footprint
of `dxfgrabber` is not noticeable and for really big files the :mod:`iterdxf` add-on does a better job.

.. _faq002:

Imported ezdxf package has no content. (readfile, new)
------------------------------------------------------

1. AttributeError: partially initialized module 'ezdxf' has no attribute 'readfile' (most likely due to a circular import)

   Did you name your file/script "ezdxf.py"? This causes problems with
   circular imports. Renaming your file/script should solve this issue.

2. AttributeError: module 'ezdxf' has no attribute 'readfile'

   This could be a hidden permission error, for more information about this issue
   read Petr Zemeks article: https://blog.petrzemek.net/2020/11/17/when-you-import-a-python-package-and-it-is-empty/

.. _faq003:

How to add/edit ACIS based entities like 3DSOLID, REGION or SURFACE
-------------------------------------------------------------------

The BODY, 3DSOLID, SURFACE, REGION and so on, are stored as ACIS data embedded
in the DXF file. The ACIS data is stored as SAT (text) format in the entity
itself for DXF R2000-R2010 and as SAB (binary) format in the
ACDSDATA section for DXF R2013+. `Ezdxf` can read SAT and SAB data, but
only write SAT data.

The ACIS data is a proprietary format from `Spatial Inc.`_, and there exist no
free available documentation or open source libraries to create or edit SAT or
SAB data, and also `ezdxf` provides no functionality for creating or editing
ACIS data.

The ACIS support provided by `ezdxf` is only useful for users have to have
access to the ACIS SDK from `Spatial Inc.`_.

.. _Spatial Inc.: https://www.spatial.com/products/3d-acis-modeling
