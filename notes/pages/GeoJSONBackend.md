docs:: <https://ezdxf.mozman.at/docs/addons/drawing.html#geojsonbackend>

- Output backend for the [[drawing add-on]]
- Creates a JSON-like output according the [[GeoJSON]] scheme.
- GeoJSON uses a geographic coordinate reference system, World Geodetic System 1984 [EPSG:4326](https://epsg.io/4326), and units of decimal degrees.
	- Latitude: -90 to +90 (South/North)
	- Longitude: -180 to +180 (East/West)
- The GeoJSON format supports only straight lines so curved shapes are flattened to
  polylines and polygons.
- The properties are handled as a foreign member feature and is therefore not defined in the GeoJSON specs.
	- It is possible to provide a custom function to create these property objects.