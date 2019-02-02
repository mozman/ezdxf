.. module:: ezdxf.ezmath

This utilities located in module :mod:`ezdxf.ezmath`::

    from ezdxf.ezmath import Matrix44


Matrix44
--------

.. class:: Matrix44

    This is a pure Python implementation for 4x4 transformation matrices, to avoid dependency to big numerical packages
    like numpy, and before binary wheels, installation of these packages wasn't always easy on Windows.

    Matrix44 initialization:

    - Matrix44() is the identity matrix.
    - Matrix44(values) values is an iterable with the 16 components of the matrix.
    - Matrix44(row1, row2, row3, row4) four rows, each row with four values.


.. method:: Matrix44.set(*args)

    Reset matrix values:

    - set() creates the identity matrix.
    - set(values) values is an iterable with the 16 components of the matrix.
    - set(row1, row2, row3, row4) four rows, each row with four values.

.. method:: Matrix44.__repr__()

    Returns the representation string of the matrix:

    ``Matrix44((col0, col1, col2, col3), (...), (...), (...))``

.. method:: Matrix44.get_row(row)

    Get row as list of of four float values.

.. method:: Matrix44.set_row(row, values)

    Sets the values in a row.

    :param row: row index [0..3]
    :param values: four column values as iterable.


.. method:: Matrix44.get_col(col)

    Get column as list of of four float values.

.. method:: Matrix44.set_col(col, values)

    Sets the values in a column.

    :param col: column index [0..3]
    :param values: four column values as iterable.

.. method:: Matrix44.copy()

.. method:: Matrix44.__copy__()

.. method:: Matrix44.scale(sx, sy=None, sz=None)

    Class method returns a scaling transformation matrix. If sy is None, sy = sx, and if sz is None sz = sx.

.. method:: Matrix44.translate(x, y, z)

    Class method returns a translation matrix to (x, y, z).

.. method:: Matrix44.x_rotate(angle)

    Class method returns a rotation matrix about the x-axis.

    :param angle: rotation angle in radians

.. method:: Matrix44.y_rotate(angle)

    Class method returns a rotation matrix about the y-axis.

    :param angle: rotation angle in radians

.. method:: Matrix44.z_rotate(angle)

    Class method returns a rotation matrix about the z-axis.

:param angle: rotation angle in radians

.. method:: Matrix44.axis_rotate(axis, angle)

    Class method returns a rotation matrix about an arbitrary axis.

    :param axis: rotation axis as (x, y, z) tuple
    :param angle: rotation angle in radians

.. method:: Matrix44.xyz_rotate(angle_x, angle_y, angle_z)

    Class method returns a rotation matrix for rotation about each axis.

    :param angle_x: rotation angle about x-axis in radians
    :param angle_y: rotation angle about y-axis in radians
    :param angle_z: rotation angle about z-axis in radians


.. method:: Matrix44.perspective_projection(left, right, top, bottom, near, far)

    Class method returns a matrix for a 2d projection.


    :param left: Coordinate of left of screen
    :param right: Coordinate of right of screen
    :param top: Coordinate of the top of the screen
    :param bottom: Coordinate of the bottom of the screen
    :param near: Coordinate of the near clipping plane
    :param far: Coordinate of the far clipping plane


.. method:: Matrix44.perspective_projection_fov(fov, aspect, near, far)

    Class method returns a matrix for a 2d projection.


    :param fov: The field of view (in radians)
    :param aspect: The aspect ratio of the screen (width / height)
    :param near: Coordinate of the near clipping plane
    :param far: Coordinate of the far clipping plane

.. method:: Matrix44.chain(*matrices)

    Compose a transformation matrix from one or more matrices.

.. method:: Matrix44.__setitem__(coord, value)

    Set (row, column) element.

.. method:: Matrix44.__getitem__(coord)

    Get (row, column) element.

.. method:: Matrix44.__iter__()

    Iterates over all matrix values.

.. method:: Matrix44.__mul__(other)

    Returns a new matrix as result of the matrix multiplication with another matrix.

.. method:: Matrix44.__imul__(other)

    Inplace multiplication with another matrix.

.. method:: Matrix44.fast_mul(other)

    Multiplies this matrix with other matrix inplace.

    Assumes that both matrices have a right column of (0, 0, 0, 1). This is True for matrices composed of
    rotations,  translations and scales. fast_mul is approximately 25% quicker than __imul__().

.. method:: Matrix44.rows()

    Iterate over rows as 4-tuples.

.. method:: Matrix44.columns()

    Iterate over columns as 4-tuples.

.. method:: Matrix44.transform(vector)

    Transforms a 3d vector and return the result as a tuple.

.. method:: Matrix44.transform_vectors(vectors)

    Returns a list of transformed vectors.

.. method:: Matrix44.transpose()

    Swaps the rows for columns inplace.

.. method:: Matrix44.get_transpose()

    Returns a new transposed matrix.

.. method:: Matrix44.determinant()

    Returns determinant.

.. method:: Matrix44.inverse()

    Returns the inverse of the matrix.

    :raises ZeroDivisionError: if matrix has no inverse.

