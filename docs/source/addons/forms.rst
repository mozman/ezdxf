.. module:: ezdxf.addons
    :noindex:

Showcase Forms
==============

MengerSponge
------------

Build a 3D `Menger sponge <https://en.wikipedia.org/wiki/Menger_sponge>`_.

.. autoclass:: MengerSponge

    .. automethod:: MengerSponge.render

    .. automethod:: MengerSponge.cubes

    .. automethod:: MengerSponge.mesh


Menger Sponge ``kind=0``:

.. image:: gfx/menger_sponge_0.png

Menger Sponge ``kind=1``:

.. image:: gfx/menger_sponge_1.png

Menger Sponge ``kind=2``:

.. image:: gfx/menger_sponge_2.png

Jerusalem Cube ``kind=3``:

.. image:: gfx/jerusalem_cube.png


SierpinskyPyramid
-----------------

Build a 3D `Sierpinsky Pyramid <https://en.wikipedia.org/wiki/Sierpinski_triangle>`_.

.. autoclass:: SierpinskyPyramid


    .. automethod:: SierpinskyPyramid.render

    .. automethod:: SierpinskyPyramid.pyramids

    .. automethod:: SierpinskyPyramid.mesh

Sierpinsky Pyramid with triangle base:

.. image:: gfx/sierpinski_pyramid_3.png

Sierpinsky Pyramid with square base:

.. image:: gfx/sierpinski_pyramid_4.png
