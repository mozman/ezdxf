.. _tut_polyface:

Tutorial for Polyface
=====================

The :class:`~ezdxf.entities.Polyface` entity represents a 3D mesh build of
vertices and faces and is just an extended POLYLINE entity with a complex
VERTEX structure. The :class:`Polyface` entity was used in DXF R12 and older
DXF versions and is still supported by newer DXF versions. The new
:class:`~ezdxf.entities.Mesh` entity stores the same data much more efficient
but requires DXF R2000 or newer. The :class:`Polyface` entity supports only
triangles and quadrilaterals as faces the :class:`Mesh` entity supports n-gons.

Its recommended to use the :class:`~ezdxf.render.MeshBuilder` objects to
create 3D meshes and render them as POLYFACE entities by the
:meth:`~ezdxf.render.MeshBuilder.render_polymesh` method into a layout:

.. code-block:: Python

        import ezdxf
        from ezdxf import colors
        from ezdxf.gfxattribs import GfxAttribs
        from ezdxf.render import forms

        cube = forms.cube().scale_uniform(10).subdivide(2)
        red = GfxAttribs(color=colors.RED)
        green = GfxAttribs(color=colors.GREEN)
        blue = GfxAttribs(color=colors.BLUE)

        doc = ezdxf.new()
        msp = doc.modelspace()

        # render as MESH entity
        cube.render(msp, dxfattribs=red)
        cube.translate(20)

        # render as POLYFACE a.k.a. POLYLINE entity
        cube.render_polyface(msp, dxfattribs=green)
        cube.translate(20)

        # render as unconnected 3DFACE entities
        cube.render_3dfaces(msp, dxfattribs=blue)

        doc.saveas("meshes.dxf")

.. warning::

    If the mesh contains n-gons the render methods for POLYFACE and
    3DFACES subdivides the n-gons into triangles, which does **not** work for
    concave faces.

The usage of the :class:`~ezdxf.render.MeshBuilder` object is also recommended
for inspecting :class:`Polyface` entities:

- :attr:`MeshBuilder.vertices` is a sequence of 3D points as
  :class:`ezdxf.math.Vec3` objects
- a face in :attr:`MeshBuilder.faces` is a sequence of indices into the
  :attr:`MeshBuilder.vertices` sequence

.. code-block:: Python

    import ezdxf
    from ezdxf.render import MeshBuilder

    def process(mesh):
        # vertices is a sequence of 3D points
        vertices = mses.vertices
        # a face is a sequence of indices into the vertices sequence
        faces = mesh.faces
        ...

    doc = ezdxf.readfile("meshes.dxf")
    msp = doc.modelspace()
    for polyline in msp.query("POLYLINE"):
        if polyline.is_poly_face_mesh:
            mesh = MeshBuilder.from_polyface(polyline)
            process(mesh)
