#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from ezdxf.acc import USE_C_EXT

# Import of Python or Cython implementations:
if USE_C_EXT:
    from ezdxf.acc.vector import (
        Vec3, Vec2, X_AXIS, Y_AXIS, Z_AXIS, NULLVEC, distance, lerp, Vector,
    )
    from ezdxf.acc.matrix44 import Matrix44
    from ezdxf.acc.bezier4p import Bezier4P
else:
    from ._vector import (
        Vec3, Vec2, X_AXIS, Y_AXIS, Z_AXIS, NULLVEC, distance, lerp, Vector,
    )
    from ._matrix44 import Matrix44
    from ._bezier4p import Bezier4P
