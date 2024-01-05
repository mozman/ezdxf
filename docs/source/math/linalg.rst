
.. module:: ezdxf.math.linalg

.. _math_linalg:

Linear Algebra
==============

Linear algebra module **for internal usage**: :mod:`ezdxf.math.linalg`

Functions
---------

.. autofunction:: tridiagonal_vector_solver

.. autofunction:: tridiagonal_matrix_solver

.. autofunction:: banded_matrix

.. autofunction:: detect_banded_matrix

.. autofunction:: compact_banded_matrix


Matrix Class
------------

.. autoclass:: Matrix

    .. autoattribute:: nrows

    .. autoattribute:: ncols

    .. autoattribute:: shape

    .. automethod:: reshape

    .. automethod:: identity

    .. automethod:: row

    .. automethod:: col

    .. automethod:: diag

    .. automethod:: rows

    .. automethod:: cols

    .. automethod:: set_row

    .. automethod:: set_col

    .. automethod:: set_diag

    .. automethod:: append_row

    .. automethod:: append_col

    .. automethod:: transpose

    .. automethod:: inverse

    .. automethod:: determinant

    .. automethod:: freeze

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __eq__

    .. automethod:: __add__

    .. automethod:: __sub__

    .. automethod:: __mul__


NumpySolver
-----------

.. autoclass:: NumpySolver

    .. automethod:: solve_vector

    .. automethod:: solve_matrix


BandedMatrixLU Class
--------------------

.. autoclass:: BandedMatrixLU

    .. attribute:: upper

        Upper triangle

    .. attribute:: lower

        Lower triangle

    .. attribute:: m1

        Lower band count, excluding main matrix diagonal

    .. attribute:: m2

        Upper band count, excluding main matrix diagonal

    .. attribute:: index

        Swapped indices

    .. autoattribute:: nrows

    .. automethod:: solve_vector

    .. automethod:: solve_matrix

    .. automethod:: determinant

.. _Gauss-Jordan: https://en.wikipedia.org/wiki/Gaussian_elimination
.. _Gauss-Elimination: https://en.wikipedia.org/wiki/Gaussian_elimination
.. _LU Decomposition: https://en.wikipedia.org/wiki/LU_decomposition
