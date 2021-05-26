from typing import Tuple, Callable

LayerName = str
Color = str
Radians = float
RGB = Tuple[int, int, int]
FilterFunc = Callable[["DXFGraphic"], bool]
