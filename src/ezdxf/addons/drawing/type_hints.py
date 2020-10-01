from typing import Tuple, TypeVar, Sequence
from ezdxf.render import Path
LayerName = str
Color = str
Radians = float
RGB = Tuple[int, int, int]

# THole represents a hole in a polygon, the first component is the outline path
# of the hole, the second component are nested holes inside of the outline
# path or an empty sequence.
THole = TypeVar('THole')
THole = Tuple[Path, Sequence[THole]]  # (outline path , [nested path, ...])
