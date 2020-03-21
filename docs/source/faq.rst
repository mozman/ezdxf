.. _faq:

FAQ
===

What is the Relationship Between ezdxf, dxfwrite and dxfgrabber?
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
:ref:`r12writer` add-on does the same job as `dxfwrite` without any in memory structures by writing direct to a stream
or file and there is also no advantage of `dxfgrabber` over `ezdxf` for normal DXF files the smaller memory footprint
of `dxfgrabber` is not noticeable and for really big files the :ref:`iterdxf` add-on does a better job.
