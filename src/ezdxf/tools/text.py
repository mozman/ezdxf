#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#  All tools in this module have to be independent from DXF entities!
import enum
from typing import (
    List, Iterable, Tuple, TYPE_CHECKING, Union, Optional, Callable, NamedTuple,
)
import re
import math

from ezdxf.lldxf import validator, const
from ezdxf.lldxf.const import (
    MTextParagraphAlignment, MTextLineAlignment, MTextStroke,
    LEFT, CENTER, RIGHT, BASELINE, BOTTOM, MIDDLE, TOP,
)
from ezdxf.math import Vec3, Vec2, Vertex
from .fonts import FontMeasurements, AbstractFont, FontFace
from .rgb import rgb2int, RGB

if TYPE_CHECKING:
    from ezdxf.eztypes import Text, MText, DXFEntity

X_MIDDLE = 4  # special case for overall alignment "MIDDLE"

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


class TextLine:
    """ Helper class which represents a single line text entity
    (e.g. :class:`~ezdxf.entities.Text`).

    Args:
        text: content string
        font: ezdxf font definition like :class:`~ezdxf.tools.fonts.MonospaceFont`
            or :class:`~ezdxf.tools.fonts.MatplotlibFont`

    """

    def __init__(self, text: str, font: 'AbstractFont'):
        self._font = font
        self._text_width: float = font.text_width(text)
        self._stretch_x: float = 1.0
        self._stretch_y: float = 1.0

    def stretch(self, alignment: str, p1: Vec3, p2: Vec3) -> None:
        """ Set stretch factors for "FIT" and "ALIGNED" alignments to fit the
        text between `p1` and `p2`, only the distance between these points is
        important. Other given `alignment` values are ignore.

        """
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
        """ Returns the final (stretched) text width. """
        return self._text_width * self._stretch_x

    @property
    def height(self) -> float:
        """ Returns the final (stretched) text height. """
        return self._font.measurements.total_height * self._stretch_y

    def font_measurements(self) -> FontMeasurements:
        """ Returns the scaled font measurements. """
        return self._font.measurements.scale(self._stretch_y)

    def baseline_vertices(self,
                          insert: Vertex,
                          halign: int = 0,
                          valign: int = 0,
                          angle: float = 0,
                          scale: Tuple[float, float] = (1, 1)) -> List[Vec3]:
        """ Returns the left and the right baseline vertex of the text line.

        Args:
            insert: insertion location
            halign: horizontal alignment left=0, center=1, right=2
            valign: vertical alignment baseline=0, bottom=1, middle=2, top=3
            angle: text rotation in radians
            scale: scale in x- and y-axis as 2-tuple of float

        """
        fm = self.font_measurements()
        vertices = [
            Vec2(0, fm.baseline),
            Vec2(self.width, fm.baseline),
        ]
        shift = self._shift_vector(halign, valign, fm)
        # Oblique angle is deliberately not supported, the base line should be
        # (near) the y-coordinate=0.
        return TextLine.transform_2d(vertices, insert, shift, angle, scale)

    def corner_vertices(self,
                        insert: Vertex,
                        halign: int = 0,
                        valign: int = 0,
                        angle: float = 0,
                        scale: Tuple[float, float] = (1, 1),
                        oblique: float = 0) -> List[Vec3]:
        """ Returns the corner vertices of the text line in the order
        bottom left, bottom right, top right, top left.

        Args:
            insert: insertion location
            halign: horizontal alignment left=0, center=1, right=2
            valign: vertical alignment baseline=0, bottom=1, middle=2, top=3
            angle: text rotation in radians
            scale: scale in x- and y-axis as 2-tuple of float
            oblique: shear angle (slanting) in x-direction in radians

        """
        fm = self.font_measurements()
        vertices = [
            Vec2(0, fm.bottom),
            Vec2(self.width, fm.bottom),
            Vec2(self.width, fm.cap_top),
            Vec2(0, fm.cap_top),
        ]
        shift = self._shift_vector(halign, valign, fm)
        return TextLine.transform_2d(
            vertices, insert, shift, angle, scale, oblique)

    def _shift_vector(self, halign: int, valign: int,
                      fm: FontMeasurements) -> Tuple[float, float]:
        return _shift_x(self.width, halign), _shift_y(fm, valign)

    @staticmethod
    def transform_2d(vertices: Iterable[Vertex],
                     insert: Vertex = Vec3(0, 0, 0),
                     shift: Tuple[float, float] = (0, 0),
                     rotation: float = 0,
                     scale: Tuple[float, float] = (1, 1),
                     oblique: float = 0) -> List[Vec3]:
        """ Transform any vertices from the text line located at the base
        location at (0, 0) and alignment "LEFT".

        Args:
            vertices: iterable of vertices
            insert: insertion location
            shift: (shift-x, shift-y) as 2-tuple of float
            rotation: text rotation in radians
            scale: (scale-x, scale-y)  as 2-tuple of float
            oblique: shear angle (slanting) in x-direction in radians

        """
        # Building a transformation matrix vs. applying transformations in
        # individual steps:
        # Most text is horizontal, because people like to read horizontal text!
        # Operating in 2D is faster than building a full 3D transformation
        # matrix and a pure 2D transformation matrix is not implemented!
        # This function doesn't transform many vertices at the same time,
        # mostly only 4 vertices, therefore the matrix multiplication overhead
        # does not pay off.
        # The most expensive rotation transformation is the least frequently
        # used transformation.
        # IMPORTANT: this assumptions are not verified by profiling!

        # Use 2D vectors:
        vertices = Vec2.generate(vertices)

        # 1. slanting at the original location (very rare):
        if oblique:
            slant_x = math.tan(oblique)
            vertices = (Vec2(v.x + v.y * slant_x, v.y) for v in vertices)

        # 2. apply alignment shifting (frequently):
        shift_vector = Vec2(shift)
        if shift_vector:
            vertices = (v + shift_vector for v in vertices)

        # 3. scale (and mirror) at the aligned location (more often):
        scale_x, scale_y = scale
        if scale_x != 1 or scale_y != 1:
            vertices = (Vec2(v.x * scale_x, v.y * scale_y) for v in vertices)

        # 4. apply rotation (rare):
        if rotation:
            vertices = (v.rotate(rotation) for v in vertices)

        # 5. move to insert location in OCS/3D! (every time)
        insert = Vec3(insert)
        return [insert + v for v in vertices]


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
    elif valign == X_MIDDLE:
        return -fm.cap_top + fm.total_height / 2
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
    if dxftype in ('TEXT', 'ATTRIB', 'ATTDEF'):
        halign = entity.dxf.halign
        valign = entity.dxf.valign
        if halign in (3, 5):  # ALIGNED=3, FIT=5
            # For the alignments ALIGNED and FIT the text stretching has to be
            # handles separately.
            halign = CENTER
            valign = BASELINE
        elif halign == 4:  # MIDDLE is different to MIDDLE/CENTER
            halign = CENTER
            valign = X_MIDDLE
        return halign, valign
    elif dxftype == 'MTEXT':
        return MTEXT_ALIGN_FLAGS.get(entity.dxf.attachment_point, (LEFT, TOP))
    else:
        raise TypeError(f"invalid DXF {dxftype}")


def plain_text(text: str) -> str:
    """ Returns the plain text for :class:`~ezdxf.entities.Text`,
    :class:`~ezdxf.entities.Attrib` and :class:`~ezdxf.entities.Attdef` content.
    """
    # TEXT, ATTRIB and ATTDEF are short strings <= 255 in R12.
    # R2000 allows 2049 chars, but this limit is not often used in real world
    # applications.
    result = ""
    scanner = TextScanner(validator.fix_one_line_text(caret_decode(text)))
    while scanner.has_data:
        char = scanner.peek()
        if char == "%":  # special characters
            if scanner.peek(1) == "%":
                code = scanner.peek(2).lower()
                letter = const.SPECIAL_CHAR_ENCODING.get(code)
                if letter:
                    scanner.consume(3)  # %%?
                    result += letter
                    continue
                elif code in "kou":
                    # formatting codes (%%k, %%o, %%u) will be ignored in
                    # TEXT, ATTRIB and ATTDEF:
                    scanner.consume(3)
                    continue
        scanner.consume(1)
        # slightly faster then "".join(chars)
        result += char
    return result


ONE_CHAR_COMMANDS = "PNLlOoKkX"


##################################################
# MTEXT inline codes
# \L	Start underline
# \l	Stop underline
# \O	Start overline
# \o	Stop overline
# \K	Start strike-through
# \k	Stop strike-through
# \P	New paragraph (new line)
# \N	New column
# \~    None breaking space
# ^I    Tabulator
# \	Escape character - e.g. \\ = "\", \{ = "{"
#
# \p    start paragraph properties until next ";"
# \pi#,l#,r#; paragraph indent
#   i#  indent first line left, relative to (l)!
#   l#  indent paragraph left
#   r#  indent paragraph right
#   q?  alignments:
#   ql  align text in paragraph: left
#   qr  align text in paragraph: right
#   qc  align text in paragraph: center
#   qj  align text in paragraph: justified
#   qd  align text in paragraph: distributed
#   x   unknown meaning
#   t#[,c#,r#...] define absolute tabulator stops 1,c2,r3...
#       without prefix is a left adjusted tab stop
#       prefix 'c' for center adjusted tab stop
#       prefix 'r' for right adjusted tab stop
#   ?*  reset command to default value
#
# Examples:
# \pi1,t[5,20,...]; define tab stops as comma separated list
# \pxt4,c8,r12,16,c20,r24; left, centered and right adjusted tab stops
# \pi*,l*,r*,q*,t; reset to default values
# \pi2,l0;  = first line  2 & paragraph left 0
# \pi-2,l2; = first line -2 & paragraph left 2
# \pi0,l2;  = first line  0 & paragraph left 2
#
# \X	Paragraph wrap on the dimension line (only in dimensions)
# \Q	Slanting (oblique) text by angle - e.g. \Q30;
# \H	Text height relative - e.g. \H3x;
# \H	Text height absolute - e.g. \H3;
# \W	Text width factor - e.g. \W0.8x;
# \W	Text width absolute - e.g. \W0.8;
# \F	Font selection
# \f	Font selection
#
#     e.g. \Fgdt;o - GDT-tolerance
#     e.g. \fArial|b0|i0|c238|p10; - font Arial, non-bold, non-italic,
#     codepage 238, pitch 10
#     codepage 0 = no change
#     pitch 0 = no change
#
# \S	Stacking, fractions
#
#     e.g. \SA^ B;
#     A
#     B
#     e.g. \SX/ Y;
#     X
#     -
#     Y
#     e.g. \S1# 4;
#     1/4
#
# \A	Alignment relative to current line
#
#     \A0; = bottom
#     \A1; = center
#     \A2; = top
#
# \C	Color change
#
#     \C1; = red
#     \C2; = yellow
#     \C3; = green
#     \C4; = cyan
#     \C5; = blue
#     \C6; = magenta
#     \C7; = white

#     \c255; = RED (255, 0, 0)
#     \c65280; = GREEN (0, 255, 0)
#     \c16711680; = BLUE (0, 0, 255)

#     RGB color = \c7528479;  = 31,224,114
#     ezdxf.rgb2int((31,224,114)) = 2089074 (r,g,b) wrong!
#     ezdxf.rgb2int((114,224,31)) = 7528479 (b,g,r) reversed order is correct!
#
# \T	Tracking, char.spacing absolute - e.g. \T2;
# \T	Tracking, char.spacing relative - e.g. \T2x;
# {}	Braces - define the text area influenced by the code
#       Multiple codes after the opening brace are valid until the closing
#       brace.  e.g. {\H0.4x;\A1;small centered text}
#
# Codes and braces can be nested up to 8 levels deep
#
# Column types in BricsCAD:
#   - dynamic auto height: all columns have the same height
#   - dynamic manual height: each columns has an individual height
#   - no columns
#   - static: all columns have the same height, like dynamic auto height,
#     difference is only important for user interaction in CAD applications
#
# - All columns have the same width and gutter.
# - Paragraphs do overflow into the next column if required.

def plain_mtext(text: str, split=False) -> Union[List[str], str]:
    """ Returns the plain MTEXT content as a single string or  a list of
    strings if `split` is ``True``. Replaces ``\\P`` by ``\\n`` and removes
    other controls chars and inline codes.

    Args:
        text: MTEXT content string
        split: split content at line endings ``\\P``

    """
    chars = []
    # split text into chars, in reversed order for efficient pop()
    raw_chars = list(reversed(text))
    while len(raw_chars):
        char = raw_chars.pop()
        if char == '\\':  # is a formatting command
            try:
                char = raw_chars.pop()
            except IndexError:
                break  # premature end of text - just ignore

            if char in '\\{}':
                chars.append(char)
            elif char in ONE_CHAR_COMMANDS:
                if char == 'P':  # new line
                    chars.append('\n')
                elif char == 'N':  # new column
                    # until columns are supported, better to at least remove the
                    # escape character
                    chars.append(' ')
                else:
                    pass  # discard other commands
            else:  # multiple character commands are terminated by ';'
                stacking = char == 'S'  # stacking command surrounds user data
                first_char = char
                search_chars = raw_chars.copy()
                try:
                    while char != ';':  # end of format marker
                        char = search_chars.pop()
                        if stacking and char != ';':
                            # append user data of stacking command
                            chars.append(char)
                    raw_chars = search_chars
                except IndexError:
                    # premature end of text - just ignore
                    chars.append('\\')
                    chars.append(first_char)
        elif char in '{}':  # grouping
            pass  # discard group markers
        elif char == '%':  # special characters
            if len(raw_chars) and raw_chars[-1] == '%':
                raw_chars.pop()  # discard next '%'
                if len(raw_chars):
                    code = raw_chars.pop()
                    letter = const.SPECIAL_CHAR_ENCODING.get(code.lower())
                    if letter:
                        chars.append(letter)
                    else:
                        chars.extend(("%", "%", code))
            else:  # char is just a single '%'
                chars.append(char)
        else:  # char is what it is, a character
            chars.append(char)

    result = "".join(chars)
    return result.split('\n') if split else result


def caret_decode(text: str) -> str:
    """ DXF stores some special characters using caret notation. This function
    decodes this notation to normalise the representation of special characters
    in the string.

    see: https://en.wikipedia.org/wiki/Caret_notation

    """

    def replace_match(match: "re.Match") -> str:
        c = ord(match.group(1))
        return chr((c - 64) % 126)

    return re.sub(r'\^(.)', replace_match, text)


def split_mtext_string(s: str, size: int = 250) -> List[str]:
    """ Split the MTEXT content string into chunks of max `size`. """
    chunks = []
    pos = 0
    while True:
        chunk = s[pos:pos + size]
        if len(chunk):
            if len(chunk) < size:
                chunks.append(chunk)
                return chunks
            pos += size
            # do not split chunks at '^'
            if chunk[-1] == '^':
                chunk = chunk[:-1]
                pos -= 1
            chunks.append(chunk)
        else:
            return chunks


def escape_dxf_line_endings(text: str) -> str:
    # replacing '\r\n' and '\n' by '\P' is required when exporting, else an
    # invalid DXF file would be created.
    return text.replace('\r', '').replace('\n', '\\P')


def replace_non_printable_characters(text: str, replacement: str = '▯') -> str:
    return ''.join(replacement if is_non_printable_char(c) else c for c in text)


def is_non_printable_char(char: str) -> bool:
    return 0 <= ord(char) < 32 and char != '\t'


def text_wrap(text: str, box_width: Optional[float],
              get_text_width: Callable[[str], float]) -> List[str]:
    """ Wrap text at ``\\n`` and given `box_width`. This tool was developed for
    usage with the MTEXT entity. This isn't the most straightforward word
    wrapping algorithm, but it aims to match the behavior of AutoCAD.

    Args:
        text: text to wrap, included ``\\n`` are handled as manual line breaks
        box_width: wrapping length, ``None`` to just wrap at ``\\n``
        get_text_width: callable which returns the width of the given string

    """
    # Copyright (c) 2020-2021, Matthew Broadway
    # License: MIT License
    if not text or text.isspace():
        return []
    manual_lines = re.split(r'(\n)', text)  # includes \n as it's own token
    tokens = [t for line in manual_lines for t in re.split(r'(\s+)', line) if t]
    lines = []
    current_line = ''
    line_just_wrapped = False

    for t in tokens:
        on_first_line = not lines
        if t == '\n' and line_just_wrapped:
            continue
        line_just_wrapped = False
        if t == '\n':
            lines.append(current_line.rstrip())
            current_line = ''
        elif t.isspace():
            if current_line or on_first_line:
                current_line += t
        else:
            if box_width is not None and get_text_width(
                    current_line + t) > box_width:
                if not current_line:
                    current_line += t
                else:
                    lines.append(current_line.rstrip())
                    current_line = t
                    line_just_wrapped = True
            else:
                current_line += t

    if current_line and not current_line.isspace():
        lines.append(current_line.rstrip())
    return lines


def is_text_vertical_stacked(text: 'DXFEntity') -> bool:
    """ Returns ``True`` if the associated text :class:`~ezdxf.entities.Textstyle`
    is vertical stacked.
    """
    if not text.is_supported_dxf_attrib('style'):
        raise TypeError(
            f'{text.dxftype()} does not support the style attribute.')

    if text.doc:
        style = text.doc.styles.get(text.dxf.style)
        if style:
            return style.is_vertical_stacked
    return False


_alignment_char = {
    MTextParagraphAlignment.DEFAULT: '',
    MTextParagraphAlignment.LEFT: 'l',
    MTextParagraphAlignment.RIGHT: 'r',
    MTextParagraphAlignment.CENTER: 'c',
    MTextParagraphAlignment.JUSTIFIED: 'j',
    MTextParagraphAlignment.DISTRIBUTED: 'd',
}

COMMA = ","
DIGITS = "01234567890"


def rstrip0(s):
    if isinstance(s, (int, float)):
        return f"{s:g}"
    else:
        return s


class ParagraphProperties(NamedTuple):
    """ Stores all known MTEXT paragraph properties in a :class:`NamedTuple`.
    Indentations and tab stops are multiples of the default text height
    :attr:`MText.dxf.char_height`. E.g. :attr:`char_height` is 0.25 and
    :attr:`indent` is 4, the real indentation is 4 x 0.25 = 1 drawing unit.
    The default tabulator stops are 4, 8, 12, ... if no tabulator stops are
    explicit defined.

    Args:
         indent (float): left indentation of the first line, relative to :attr:`left`,
            which means an :attr:`indent` of 0 has always the same indentation
            as :attr:`left`
         left (float): left indentation of the paragraph except for the first line
         right (float): left indentation of the paragraph
         align: :class:`~ezdxf.lldxf.const.MTextParagraphAlignment` enum
         tab_stops: tuple of tabulator stops, as ``int`` or as ``str``, ``int``
            values are left aligned tab stops, strings with prefix ``"c"`` are
            center aligned tab stops and strings with prefix ``"r"`` are right
            aligned tab stops

    """
    # Reset: \pi*,l*,r*,q*,t;
    indent: float = 0  # relative to left!
    left: float = 0
    right: float = 0
    align: MTextParagraphAlignment = MTextParagraphAlignment.DEFAULT
    # tab stops without prefix or numbers are left adjusted
    # tab stops, e.g 2 or '2'
    # prefix 'c' defines a center adjusted tab stop e.g. 'c3.5'
    # prefix 'r' defines a right adjusted tab stop e.g. 'r2.7'
    # The tab stop in drawing units = n x char_height
    tab_stops: Tuple = tuple()

    def tostring(self) -> str:
        """ Returns the MTEXT paragraph properties as MTEXT inline code
        e.g. ``"\\pxi-2,l2;"``.

        """
        args = []
        if self.indent:
            args.append(f"i{self.indent:g}")
            args.append(COMMA)
        if self.left:
            args.append(f"l{self.left:g}")
            args.append(COMMA)
        if self.right:
            args.append(f"r{self.right:g}")
            args.append(COMMA)
        if self.align:
            args.append(f"q{_alignment_char[self.align]}")
            args.append(COMMA)
        if self.tab_stops:
            args.append(f"t{COMMA.join(map(rstrip0, self.tab_stops))}")
            args.append(COMMA)

        if args:
            if args[-1] == COMMA:
                args.pop()
            # exporting always "x" as second letter seems to be safe
            return "\\px" + "".join(args) + ";"
        else:
            return ""


# IMPORTANT for parsing MTEXT inline codes: "\\H0.1\\A1\\C1rot"
# Inline commands with a single argument, don't need a trailing ";"!


class MTextEditor:
    """ The :class:`MtextEditor` is a helper class to build MTEXT content
    strings with support for inline codes to change color, font or
    paragraph properties. The result is always accessible by the :attr:`text`
    attribute or the magic :func:`__str__` function as
    :code:`str(MTextEditor("text"))`.

    All text building methods return `self` to implement a floating interface::

        e = MTextEditor("This example ").color("red").append("switches color to red.")
        mtext = msp.add_mtext(str(e))

    The initial text height, color, text style and so on is determined by the
    DXF attributes of the :class:`~ezdxf.entities.MText` entity.

    .. warning::

        The :class:`MTextEditor` assembles just the inline code, which has to be
        parsed and rendered by the target CAD application, `ezdxf` has no influence
        to that result.

        Keep inline formatting as simple as possible, don't test the limits of its
        capabilities, this will not work across different CAD applications and keep
        the formatting in a logic manner like, do not change paragraph properties
        in the middle of a paragraph.

        **There is no official documentation for the inline codes!**

    Args:
        text: init value of the MTEXT content string.

    """

    def __init__(self, text: str = ""):
        self.text = str(text)

    NEW_LINE = r'\P'
    NEW_PARAGRAPH = r'\P'
    NEW_COLUMN = r'\N'
    UNDERLINE_START = r'\L'
    UNDERLINE_STOP = r'\l'
    OVERSTRIKE_START = r'\O'
    OVERSTRIKE_STOP = r'\o'
    STRIKE_START = r'\K'
    STRIKE_STOP = r'\k'
    GROUP_START = '{'
    GROUP_END = '}'
    ALIGN_BOTTOM = r'\A0;'
    ALIGN_MIDDLE = r'\A1;'
    ALIGN_TOP = r'\A2;'
    NBSP = r'\~'  # non breaking space
    TAB = '^I'

    def append(self, text: str) -> 'MTextEditor':
        """ Append `text`. """
        self.text += text
        return self

    def __iadd__(self, text: str) -> 'MTextEditor':
        """
        Append `text`::

            e = MTextEditor("First paragraph.\P")
            e += "Second paragraph.\P")

        """
        self.text += text
        return self

    def __str__(self) -> str:
        """ Returns the MTEXT content attribute :attr:`text`. """
        return self.text

    def clear(self):
        """ Reset the content to an empty string. """
        self.text = ""

    def font(self, name: str, bold: bool = False,
             italic: bool = False) -> 'MTextEditor':
        """ Set the text font by the font family name. Changing the font height
        should be done by the :meth:`height` or the :meth:`scale_height` method.
        The font family name is the name shown in font selection widgets in
        desktop applications: "Arial", "Times New Roman", "Comic Sans MS".
        Switching the codepage is not supported.

        Args:
            name: font family name
            bold: flag
            italic: flag

        """
        # c0 = current codepage
        # The current implementation of ezdxf writes everything in one
        # encoding, defined by $DWGCODEPAGE < DXF R2007 or utf8 for DXF R2007+
        # Switching codepage makes no sense!
        # p0 = current text size
        # Text size should be changed by \H<factor>x;
        return self.append(rf"\f{name}|b{int(bold)}|i{int(italic)};")

    def scale_height(self, factor: float) -> 'MTextEditor':
        """ Scale the text height by a `factor`. This scaling will accumulate,
        which means starting at height 2.5 and scaling by 2 and again by 3 will
        set the text height to 2.5 x 2 x 3 = 15. The current text height is not
        stored in the :class:`MTextEditor`, you have to track the text height by
        yourself! The initial text height is stored in the
        :class:`~ezdxf.entities.MText` entity as DXF attribute
        :class:`~ezdxf.entities.MText.dxf.char_height`.

        """
        return self.append(rf'\H{round(factor, 3)}x;')

    def height(self, height: float) -> 'MTextEditor':
        """ Set the absolute text height in drawing units. """
        return self.append(rf'\H{round(height, 3)};')

    def width_factor(self, factor: float) -> 'MTextEditor':
        """ Set the absolute text width factor. """
        return self.append(rf'\W{round(factor, 3)};')

    def char_tracking_factor(self, factor: float) -> 'MTextEditor':
        """ Set the absolute character tracking factor. """
        return self.append(rf'\T{round(factor, 3)};')

    def oblique(self, angle: int) -> 'MTextEditor':
        """ Set the text oblique angle in degrees, vertical is 0, a value of 15
        will lean the text 15 degree to the right.

        """
        return self.append(rf'\Q{int(angle)};')

    def color(self, name: str) -> 'MTextEditor':
        """ Set the text color by color name: "red", "yellow", "green", "cyan",
        "blue", "magenta" or "white".

        """
        return self.aci(const.MTEXT_COLOR_INDEX[name.lower()])

    def aci(self, aci: int) -> 'MTextEditor':
        """ Set the text color by :ref:`ACI` in range [0, 256].
        """
        if 0 <= aci <= 256:
            return self.append(rf"\C{aci};")
        else:
            raise ValueError("aci not in range [0, 256]")

    def rgb(self, rgb: RGB) -> 'MTextEditor':
        """ Set the text color as RGB value. """
        r, g, b = rgb
        return self.append(rf"\c{rgb2int((b, g, r))};")

    def stack(self, upr: str, lwr: str, t: str = "^") -> 'MTextEditor':
        r""" Append stacked text `upr` over `lwr`, argument `t` defines the
        kind of stacking, the space " " after the "^" will be added
        automatically to avoid caret decoding:

        .. code-block:: none

            "^": vertical stacked without divider line, e.g. \SA^ B:
                 A
                 B

            "/": vertical stacked with divider line,  e.g. \SX/Y:
                 X
                 -
                 Y

            "#": diagonal stacked, with slanting divider line, e.g. \S1#4:
                 1/4

        """
        if t not in "^/#":
            raise ValueError(f"invalid type symbol: {t}")
        # space " " after "^" is required to avoid caret decoding
        if t == "^":
            t += " "
        return self.append(rf"\S{upr}{t}{lwr};")

    def group(self, text: str) -> 'MTextEditor':
        """ Group `text`, all properties changed inside a group are reverted at
        the end of the group. AutoCAD supports grouping up to 8 levels.

        """
        return self.append(f"{{{text}}}")

    def underline(self, text: str) -> 'MTextEditor':
        """ Append `text` with a line below the text. """
        return self.append(rf"\L{text}\l")

    def overline(self, text: str) -> 'MTextEditor':
        """ Append `text` with a line above the text. """
        return self.append(rf"\O{text}\o")

    def strike_through(self, text: str) -> 'MTextEditor':
        """ Append `text` with a line through the text. """
        return self.append(rf"\K{text}\k")

    def paragraph(self, props: ParagraphProperties) -> 'MTextEditor':
        """ Set paragraph properties by a :class:`ParagraphProperties` object.
        """
        return self.append(props.tostring())

    def bullet_list(self, indent: float, bullets: Iterable[str],
                    content: Iterable[str]) -> 'MTextEditor':
        """ Build bulleted lists by utilizing paragraph indentation and a
        tabulator stop. Any string can be used as bullet. Indentation is
        a multiple of the initial MTEXT char height (see also docs about
        :class:`ParagraphProperties`), which means indentation in
        drawing units is :attr:`MText.dxf.char_height` x `indent`.

        Useful UTF bullets:

        - "bull" U+2022 = • (Alt Numpad 7)
        - "circle" U+25CB = ○ (Alt Numpad 9)

        For numbered lists just use numbers as bullets::

            MTextEditor.bullet_list(
                indent=2,
                bullets=["1.", "2."],
                content=["first", "second"],
            )

        Args:
            indent: content indentation as multiple of the initial MTEXT char height
            bullets: iterable of bullet strings, e.g. :code:`["-"] * 3`,
                for 3 dashes as bullet strings
            content: iterable of list item strings, one string per list item,
                list items should not contain new line or new paragraph commands.

        """
        items = MTextEditor().paragraph(ParagraphProperties(
            indent=-indent * .75,  # like BricsCAD
            left=indent,
            tab_stops=(indent,)
        ))
        items.append(
            "".join(b + self.TAB + c + self.NEW_PARAGRAPH
                    for b, c in zip(bullets, content))
        )
        return self.group(str(items))


class MTextContext:
    """ Internal class to store the MTEXT context state. """

    def __init__(self):
        self._stroke: int = 0
        self._aci = 7  # used if rgb is None
        self.rgb: Optional[RGB] = None  # overrules aci
        self.align: MTextLineAlignment = MTextLineAlignment.BOTTOM
        self.font_face: FontFace = FontFace()  # is immutable
        self.cap_height: float = 1.0
        self.width_factor: float = 1.0
        self.char_tracking_factor: float = 1.0
        self.oblique: float = 0.0
        self.paragraph = ParagraphProperties()

    def __copy__(self) -> 'MTextContext':
        p = MTextContext()
        p._stroke = self._stroke
        p._aci = self._aci
        p.rgb = self.rgb
        p.align = self.align
        p.font_face = self.font_face  # is immutable
        p.cap_height = self.cap_height
        p.width_factor = self.width_factor
        p.char_tracking_factor = self.char_tracking_factor
        p.oblique = self.oblique
        p.paragraph = self.paragraph  # is immutable
        return p

    copy = __copy__

    def __hash__(self):
        return hash(
            (self._stroke, self._aci, self.rgb, self.align, self.font_face,
             self.cap_height, self.width_factor, self.char_tracking_factor,
             self.oblique, self.paragraph)
        )

    def __eq__(self, other: 'MTextContext') -> bool:
        return hash(self) == hash(other)

    @property
    def aci(self) -> int:
        return self._aci

    @aci.setter
    def aci(self, aci: int):
        if 0 <= aci <= 256:
            self._aci = aci
            self.rgb = None  # clear rgb
        else:
            raise ValueError('aci not in range[0,256]')

    def _set_stroke_state(self, stroke: MTextStroke,
                          state: bool = True) -> None:
        """ Set/clear binary `stroke` flag in `self._stroke`.

        Args:
            stroke: set/clear stroke flag
            state: ``True`` for setting, ``False`` for clearing

        """
        if state:
            self._stroke |= stroke
        else:
            self._stroke &= ~stroke

    @property
    def underline(self) -> bool:
        return bool(self._stroke & MTextStroke.UNDERLINE)

    @underline.setter
    def underline(self, value: bool) -> None:
        self._set_stroke_state(MTextStroke.UNDERLINE, value)

    @property
    def strike_through(self) -> bool:
        return bool(self._stroke & MTextStroke.STRIKE_THROUGH)

    @strike_through.setter
    def strike_through(self, value: bool) -> None:
        self._set_stroke_state(MTextStroke.STRIKE_THROUGH, value)

    @property
    def overline(self) -> bool:
        return bool(self._stroke & MTextStroke.OVERLINE)

    @overline.setter
    def overline(self, value: bool) -> None:
        self._set_stroke_state(MTextStroke.OVERLINE, value)


class TextScanner:
    __slots__ = ("_text", "_text_len", "_index")

    def __init__(self, text: str):
        self._text = str(text)
        self._text_len = len(self._text)
        self._index = 0

    @property
    def is_empty(self) -> bool:
        return self._index >= self._text_len

    @property
    def has_data(self) -> bool:
        return self._index < self._text_len

    def get(self) -> str:
        char = self.peek()
        self.consume(1)
        return char

    def consume(self, count: int = 1) -> None:
        if count < 1:
            raise ValueError(count)
        self._index += count

    def peek(self, offset: int = 0) -> str:
        if offset < 0:
            raise ValueError(offset)
        try:
            return self._text[self._index + offset]
        except IndexError:
            return ""


class TokenType(enum.IntEnum):
    NONE = 0
    WORD = 1  # data = str
    STACK = 2  # data = upr, lwr, type; upr&lwr:=(str|space)+
    SPACE = 3  # data = None
    NBSP = 4  # data = None
    TABULATOR = 5  # data = None
    NEW_PARAGRAPH = 6  # data = None
    NEW_COLUMN = 7  # data = None
    WRAP_AT_DIMLINE = 8  # data = None


class MTextToken:
    def __init__(self, t: TokenType, ctx: MTextContext, data=None):
        self.type: TokenType = t
        self.ctx: MTextContext = ctx
        self.data = data


class MTextParser:
    """ Parses the MText content string and yields the content as tokens and
    the current MText properties as MTextContext object. The context object is
    treated internally as immutable object and should be treated by the client
    the same way.

    The parser works as iterator and yields MTextToken objects.

    Args:
        content: MText content string
        ctx: initial MText context

    """

    def __init__(self, content: str, ctx: MTextContext = None):
        if ctx is None:
            ctx = MTextContext()
        self.ctx = ctx
        self.scanner = TextScanner(content)
        self._ctx_stack = []

    def __next__(self) -> MTextToken:
        type_, data = self.next_token()
        if type_:
            return MTextToken(type_, self.ctx, data)
        else:
            raise StopIteration

    def __iter__(self):
        return self

    def push_ctx(self) -> None:
        self._ctx_stack.append(self.ctx)

    def pop_ctx(self) -> None:
        if self._ctx_stack:
            self.ctx = self._ctx_stack.pop()

    def next_token(self):
        def word_or_token(token, consume: int = 1):
            if word:
                return TokenType.WORD, word
            else:
                scanner.consume(consume)
                return token, None

        word = ""
        scanner = self.scanner
        while scanner.has_data:
            escape = False
            letter = scanner.peek()
            if letter == "\\" and scanner.peek(1) in "\\{}":
                # escape next letter
                escape = True
                scanner.consume()  # leading backslash
                letter = scanner.peek()

            if letter == "\\" and not escape:
                # A non escaped backslash is always the end of a word.
                if word:
                    # Do not consume backslash!
                    return TokenType.WORD, word
                scanner.consume()  # leading backslash
                cmd = scanner.get()
                if cmd == "~":
                    return TokenType.NBSP, None
                if cmd == "P":
                    return TokenType.NEW_PARAGRAPH, None
                if cmd == "N":
                    return TokenType.NEW_COLUMN, None
                if cmd == "X":
                    return TokenType.WRAP_AT_DIMLINE, None
                if cmd == "S":
                    return self.parse_stacking()
                if cmd:
                    self.parse_properties(cmd)
                # else: A single backslash at the end is an error, but DXF
                # content is often invalid and should be ignored silently, if no
                # harm is done.
                continue

            if letter == "^":  # caret decode
                following_letter = scanner.peek(1)
                if following_letter == "I":
                    return word_or_token(TokenType.TABULATOR, consume=2)
                if following_letter == "J":  # LF
                    return word_or_token(TokenType.NEW_PARAGRAPH, consume=2)
                if following_letter == "M":  # ignore CR
                    scanner.consume(2)
                    continue
            if letter == "%" and scanner.peek(1) == "%":
                code = scanner.peek(2).lower()
                special_char = const.SPECIAL_CHAR_ENCODING.get(code)
                if special_char:
                    scanner.consume(2)  # %%
                    letter = special_char
            if letter == " ":
                return word_or_token(TokenType.SPACE)
            if letter == "{" and not escape:
                if word:
                    return TokenType.WORD, word
                else:
                    scanner.consume(1)
                    self.push_ctx()
                    continue
            if letter == "}" and not escape:
                if word:
                    return TokenType.WORD, word
                else:
                    scanner.consume(1)
                    self.pop_ctx()
                    continue

            # any unparsed unicode letter can be used in a word
            scanner.consume(1)
            if ord(letter[0]) > 31:
                word += letter

        if word:
            return TokenType.WORD, word
        else:
            return TokenType.NONE, None

    def parse_stacking(self) -> Tuple:
        scanner = self.scanner
        return TokenType.STACK, ("NUMERATOR", "DENOMINATOR", "^")

    def parse_properties(self, cmd: str) -> None:
        # Treat the existing context as immutable, create a new one:
        new_ctx = self.ctx.copy()
        if cmd == 'L':
            new_ctx.underline = True
        elif cmd == 'l':
            new_ctx.underline = False
        elif cmd == 'O':
            new_ctx.overline = True
        elif cmd == 'o':
            new_ctx.overline = False
        elif cmd == 'K':
            new_ctx.strike_through = True
        elif cmd == 'k':
            new_ctx.strike_through = False
        elif cmd == 'A':  # cell alignment A0=bottom, A1=middle, A2=top
            if not self.parse_align(new_ctx):
                return
        else:  # unknown commands
            return
        self.ctx = new_ctx

    def parse_align(self, ctx: MTextContext) -> bool:
        arg = self.parse_required_char(choices={"0", "1", "2"}, default="0")
        ctx.align = MTextLineAlignment(int(arg))
        return True

    def parse_required_char(self, choices: set, default: str) -> str:
        scanner = self.scanner
        if scanner.is_empty:
            return default
        char = scanner.get()  # always consume next char
        if char in choices:
            result = char
        else:
            result = default
        self.consume_optional_terminator()
        return result

    def consume_optional_terminator(self):
        if self.scanner.peek() == ";":
            self.scanner.consume(1)
