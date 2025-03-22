tags:: faq

- ## It's the OCS
- The ``ARC`` and other 2D entities are located in the Object Coordinate System ``OCS``.
- The ``OCS`` is used to place 2D entities in 3D space.
- A description of the ``OCS`` can be found [here](https://ezdxf.mozman.at/docs/concepts/ocs.html).
- The ``OCS`` is defined by the extrusion vector and an elevation value.
- The default ``OCS`` is defined by an extrusion vector of (0, 0, 1), that means the extrusion vector is aligned to the ``WCS`` z-axis and the ``OCS`` is coincident to the ``WCS``, in simpler words: ``OCS`` coordinates are ``WCS`` coordinates.
-
- ## When should you care about OCS coordinates?
- When the extrusion vector ``Arc.dxf.extrusion`` is (0, 0, -1) you are dealing with an inverted ``OCS``.
	- Even pure 2D drawings can contain inverted ``OCS`` as a result of mirror operations.
	- ``ezdxf`` has a special module called [upright](https://ezdxf.mozman.at/docs/upright.html) to flip inverted ``OCS`` and align them with the ``WCS``.
	- ```Python
	  from ezdxf import upright
	  
	  upright.upright(entity)  # or
	  upright.upright_all(msp)  # to apply the function to all entities in a collection
	  ```
	- The function can be called on any entity, even multiple times, without raising an error - only inverted ``OCS`` will be flipped.
	- The extrusion vector should be (0, 0, 1) now and the ``OCS`` is aligned with the ``WCS``.
	- Text based entity types can not be flipped!
- In all other cases you have to convert ``OCS`` coordinates to ``WCS`` coordinates:
	- ```Python
	  ocs = arc.ocs()
	  wcs_center = ocs.to_wcs(arc.dxf.center)  # center.z defines the elevation
	  ```
- The start- and end angles of the arc are counter-clockwise oriented around the ``OCS`` z-axis (extrusion vector) and starting at the ``OCS`` x-axis defined by the ``Arbitrary Axis Algorithm``.
- A point on ``ARC`` calculation is done in ``OCS`` coordinates and converted to ``WCS`` coordinates:
	- ```Python
	  import math
	  from ezdxf.math import Vec3
	  
	  radius = arc.dxf.radius
	  center = Vec3(arc.dxf.center)  # center.z defines the elevation
	  angle = arc.dxf.start_angle  # in degrees
	  ocs_point = center + Vec3.from_deg_angle(angle, radius)
	  ocs = arc.ocs()
	  wcs_point = ocs.to_wcs(ocs_point)
	  ```
- ## Documentation
	- [Object Coordinate System](https://ezdxf.mozman.at/docs/concepts/ocs.html)
		- [DXF Reference](https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-D99F1509-E4E4-47A3-8691-92EA07DC88F5)
		- [Arbitrary Axis Algorithm](https://ezdxf.mozman.at/docs/concepts/ocs.html#arbitrary-axis-algorithm)
	- [Tutorial for OCS/UCS Usage](https://ezdxf.mozman.at/docs/tutorials/ocs_usage.html)
	- [OCS](https://ezdxf.mozman.at/docs/math/core.html#ocs-class) Class