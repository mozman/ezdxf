.. _geo_addon:

.. module:: ezdxf.addons.geo

Geo Interface
=============

This module provides support for the  :code:`__geo_interface__`:
https://gist.github.com/sgillies/2217756

High Level Interface
--------------------

.. autofunction:: proxy

.. autofunction:: mapping

.. autofunction:: collection

.. autofunction:: gfilter

.. autofunction:: transform_wcs_to_crs

.. autofunction:: transform_crs_to_wcs


Low Level Interface
-------------------

.. autofunction:: mappings

.. autofunction:: point_mapping

.. autofunction:: line_string_mapping

.. autofunction:: polygon_mapping

.. autofunction:: join_multi_single_type_mappings

.. autofunction:: geometry_collection_mapping

.. autofunction:: linear_ring

