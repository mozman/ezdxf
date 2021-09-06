Storing User Data
=================

This section describes how to store arbitrary user data in DXF files using
standard DXF features.

Saving data in comments is not covered in this section, because comments are not
a reliable way to store information in DXF files and `ezdxf` does not support
adding comments to DXF files. Comments are also ignored by `ezdxf` and many
other DXF libraries when loading DXF files, but there is a :mod:`ezdxf.comments`
module to load comments from DXF files.

The DXF data format is a very versatile and flexible data format and supports
various ways to store user data. This starts by setting special header variables,
storing XData, AppData and extension dictionaries in DXF entities and objects,
storing XRecords in the OBJECTS section and ends by using proxy entities or
even extending the DXF format by user defined entities and objects.

Retrieving User Data
====================

Retrieving the is a simple task by `ezdxf`, but often not possible in CAD
applications without using the scripting features (AutoLisp) or even the SDK.

.. warning::

    Here you will not find any documentation about how to use the stored
    user data outside of `ezdxf`. I have no experience with AutoLisp and
    therefore there are no examples how to read and use the user data in
    AutoCAD or any other CAD application.

Header Section
==============

Meta Data
=========

XDATA
=====

AppData
=======

Extension Dictionaries
======================

XRecord
=======

UserRecord
==========

.. module:: ezdxf.urecord

