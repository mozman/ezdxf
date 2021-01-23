#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import List, Iterable, Tuple, TYPE_CHECKING, Union
from ezdxf.math import Vec3
import abc

if TYPE_CHECKING:
    from ezdxf.eztypes import Text, MText

DESCENDER_FACTOR = 0.333  # from TXT SHX font - just guessing
X_HEIGHT_FACTOR = 0.666  # from TXT SHX font - just guessing
LEFT = 0
CENTER = 1
RIGHT = 2
BASELINE = 0
BOTTOM = 1
MIDDLE = 2
TOP = 3

MTEXT_ALIGN_FLAGS = {
    1: (LEFT, TOP),
    2: (CENTER, TOP),
    3: (RIGHT, TOP),
    4: (LEFT, MIDDLE),
    5: (CENTER, MIDDLE),
    6: (RIGHT, MIDDLE),
    7: (LEFT, BOTTOM),
    8: (CENTER, BOTTOM),
    9: (RIGHT, BOTTOM),
}


class FontMeasurements:
    def __init__(self, baseline: float, cap_height: float, x_height: float,
                 descender_height: float):
        self.baseline = baseline
        self.cap_height = cap_height
        self.x_height = x_height
        self.descender_height = descender_height

    def __eq__(self, other):
        return (isinstance(other, FontMeasurements) and
                self.baseline == other.baseline and
                self.cap_height == other.cap_height and
                self.x_height == other.x_height and
                self.descender_height == other.descender_height)

    def scale(self, factor: float = 1.0) -> 'FontMeasurements':
        return FontMeasurements(
            self.baseline * factor,
            self.cap_height * factor,
            self.x_height * factor,
            self.descender_height * factor
        )

    def shift(self, distance: float = 0.0) -> 'FontMeasurements':
        return FontMeasurements(
            self.baseline + distance,
            self.cap_height,
            self.x_height,
            self.descender_height
        )

    def scale_from_baseline(
            self, desired_cap_height: float) -> 'FontMeasurements':
        factor = desired_cap_height / self.cap_height
        return FontMeasurements(
            self.baseline,
            self.cap_height * factor,
            self.x_height * factor,
            self.descender_height * factor
        )

    @property
    def cap_top(self) -> float:
        return self.baseline + self.cap_height

    @property
    def x_top(self) -> float:
        return self.baseline + self.x_height

    @property
    def bottom(self) -> float:
        return self.baseline - self.descender_height

    @property
    def total_height(self) -> float:
        return self.cap_height + self.descender_height


class AbstractFont:
    def __init__(self, measurements: FontMeasurements):
        self.measurements = measurements

    @abc.abstractmethod
    def text_width(self, text: str) -> float:
        pass


class MonospaceFont(AbstractFont):
    def __init__(self,
                 cap_height: float,
                 width_factor: float = 1.0,
                 baseline: float = 0,
                 descender_factor: float = DESCENDER_FACTOR,
                 x_height_factor: float = X_HEIGHT_FACTOR):
        super().__init__(FontMeasurements(
            baseline=baseline,
            cap_height=cap_height,
            x_height=cap_height * x_height_factor,
            descender_height=cap_height * descender_factor,
        ))
        self._width_factor: float = abs(width_factor)

    def text_width(self, text: str) -> float:
        return len(text) * self.measurements.cap_height * self._width_factor


class TextLine:
    def __init__(self, text: str, font: 'AbstractFont'):
        self._font = font
        self._text_width: float = font.text_width(text)
        self._stretch_x: float = 1.0
        self._stretch_y: float = 1.0

    def stretch(self, alignment: str, p1: Vec3, p2: Vec3) -> None:
        sx: float = 1.0
        sy: float = 1.0
        if alignment in ('FIT', 'ALIGNED'):
            defined_length: float = (p2 - p1).magnitude
            if self._text_width > 1e-9:
                sx = defined_length / self._text_width
                if alignment == 'ALIGNED':
                    sy = sx
        self._stretch_x = sx
        self._stretch_y = sy

    @property
    def width(self) -> float:
        return self._text_width * self._stretch_x

    @property
    def height(self) -> float:
        return self._font.measurements.total_height * self._stretch_y

    def font_measurements(self) -> FontMeasurements:
        return self._font.measurements.scale(self._stretch_y)

    def baseline_vertices(self, insert: Vec3, halign: int = 0, valign: int = 0,
                          angle: float = 0) -> List[Vec3]:
        """ Returns the left and the right baseline vertex of the text line.

        Args:
            insert: insertion point
            halign: horizontal alignment left=0, center=1, right=2
            valign: vertical alignment baseline=0, bottom=1, middle=2, top=3
            angle: text rotation in radians

        """
        fm = self.font_measurements()
        vertices = [
            Vec3(0, fm.baseline),
            Vec3(self.width, fm.baseline),
        ]
        shift = self._shift_vector(halign, valign, fm)
        return _transform(vertices, insert, shift, angle)

    def corner_vertices(self, insert: Vec3, halign: int = 0, valign: int = 0,
                        angle: float = 0) -> List[Vec3]:
        """ Returns the corner vertices of the text line in the order
        bottom left, bottom right, top right, top left.

        Args:
            insert: insertion point
            halign: horizontal alignment left=0, center=1, right=2
            valign: vertical alignment baseline=0, bottom=1, middle=2, top=3
            angle: text rotation in radians

        """
        fm = self.font_measurements()
        vertices = [
            Vec3(0, fm.bottom),
            Vec3(self.width, fm.bottom),
            Vec3(self.width, fm.cap_top),
            Vec3(0, fm.cap_top),
        ]
        shift = self._shift_vector(halign, valign, fm)
        return _transform(vertices, insert, shift, angle)

    def _shift_vector(self, halign: int, valign: int,
                      fm: FontMeasurements) -> Vec3:
        return Vec3(
            _shift_x(self.width, halign),
            _shift_y(fm, valign)
        )


def _transform(vertices: Iterable[Vec3],
               insert: Vec3,
               shift: Vec3,
               rotation: float) -> List[Vec3]:
    return [insert + (v + shift).rotate(rotation) for v in vertices]


def _shift_x(total_width: float, halign: int) -> float:
    if halign == CENTER:
        return -total_width / 2.0
    elif halign == RIGHT:
        return -total_width
    return 0.0  # LEFT


def _shift_y(fm: FontMeasurements, valign: int) -> float:
    if valign == BASELINE:
        return fm.baseline
    elif valign == MIDDLE:
        return -fm.cap_top + fm.cap_height / 2
    elif valign == TOP:
        return -fm.cap_top
    return -fm.bottom


def unified_alignment(entity: Union['Text', 'MText']) -> Tuple[int, int]:
    """ Return unified horizontal and vertical alignment.

    horizontal alignment: left=0, center=1, right=2

    vertical alignment: baseline=0, bottom=1, middle=2, top=3

    Returns:
        tuple(halign, valign)

    """
    dxftype = entity.dxftype()
    if dxftype == 'TEXT':
        halign = entity.dxf.halign
        valign = entity.dxf.valign
        if halign > 2:  # ALIGNED=3, MIDDLE=4, FIT=5
            # For the alignments ALIGNED and FIT the text stretching has to be
            # handles separately.
            halign = CENTER
            valign = BASELINE
        # Special alignment MIDDLE is handles as (CENTER, MIDDLE)
        if halign == 4:
            valign = MIDDLE
        return halign, valign
    elif dxftype == 'MTEXT':
        return MTEXT_ALIGN_FLAGS.get(entity.dxf.attachment_point, (LEFT, TOP))
    else:
        raise TypeError(f"invalid DXF {dxftype}")
