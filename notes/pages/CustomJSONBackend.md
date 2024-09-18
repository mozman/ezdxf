docs:: <https://ezdxf.mozman.at/docs/addons/drawing.html#customjsonbackend>

- Output backend for the [[drawing add-on]]
- Creates a JSON-like output with a custom JSON scheme.
- This scheme supports curved shapes by a SVG-path like structure and coordinates are not limited in
  any way.
- This backend can be used to send geometries from a web-backend to a frontend.
- The JSON scheme is documented in the source code:
	- <https://github.com/mozman/ezdxf/blob/master/src/ezdxf/addons/drawing/json.py>