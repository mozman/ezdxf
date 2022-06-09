.. module:: ezdxf.addons.openscad

OpenSCAD
========

.. versionadded:: 0.18


Interface to the `OpenSCAD`_ application to apply boolean operations to
:class:`~ezdxf.render.MeshBuilder` objects. For more information about boolean
operations read the documentation of `OpenSCAD`_. The `OpenSCAD`_ application is
not bundled with `ezdxf`, you need to install the application yourself.

Example:

.. code-block:: Python

    import ezdxf
    from ezdxf.render import forms
    from ezdxf.addons import MengerSponge, openscad

    doc = ezdxf.new()
    msp = doc.modelspace()

    # 1. create the meshes:
    sponge = MengerSponge(level=3).mesh()
    sponge.flip_normals()  # important for OpenSCAD
    sphere = forms.sphere(
        count=32, stacks=16, radius=0.5, quads=True
    ).translate(0.25, 0.25, 1)
    sphere.flip_normals()  # important for OpenSCAD

    # 2. create the script:
    script = openscad.boolean_operation(openscad.DIFFERENCE, sponge, sphere)

    # 3. execute the script by OpenSCAD:
    result = openscad.run(script)

    # 4. render the MESH entity:
    result.render_mesh(msp)

    doc.set_modelspace_vport(6, center=(5, 0))
    doc.saveas("OpenSCAD.dxf")

.. image:: gfx/openscad_menger_minus_sphere.png
    :align: center


Functions
---------

.. autofunction:: run

.. autofunction:: boolean_operation

.. autofunction:: is_installed

.. class:: Script

    Helper class to build OpenSCAD scripts.

    .. automethod:: add

    .. automethod:: add_mirror

    .. automethod:: add_multmatrix

    .. automethod:: add_polyhedron

    .. automethod:: add_resize

    .. automethod:: add_rotate

    .. automethod:: add_rotate_about_axis

    .. automethod:: add_scale

    .. automethod:: add_translate

    .. automethod:: get_string

Boolean Operation Constants
---------------------------

.. attribute:: UNION

.. attribute:: DIFFERENCE

.. attribute:: INTERSECTION

.. _OpenSCAD: https://openscad.org