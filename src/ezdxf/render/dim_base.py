# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Iterable, Optional
from ezdxf.math import Vec3, Vec2, ConstructionLine, ConstructionBox
from ezdxf.math import UCS, PassTroughUCS, xround, Z_AXIS
from ezdxf.lldxf import const
from ezdxf._options import options
from ezdxf.lldxf.const import DXFValueError, DXFUndefinedBlockError
from ezdxf.tools import suppress_zeros
from ezdxf.render.arrows import ARROWS
from ezdxf.entities.dimstyleoverride import DimStyleOverride

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        Dimension, Vertex, Drawing, GenericLayoutType, Textstyle,
    )


class TextBox(ConstructionBox):
    """ Text boundaries representation. """

    def __init__(self, center: 'Vertex', width: float, height: float,
                 angle: float, gap: float = 0):
        height += (2 * gap)
        super().__init__(center, width, height, angle)


PLUS_MINUS = '±'
_TOLERANCE_COMMON = r"\A{align};{txt}{{\H{fac:.2f}x;"
TOLERANCE_TEMPLATE1 = _TOLERANCE_COMMON + r"{tol}}}"
TOLERANCE_TEMPLATE2 = _TOLERANCE_COMMON + r"\S{upr}^ {lwr};}}"
LIMITS_TEMPLATE = r"{{\H{fac:.2f}x;\S{upr}^ {lwr};}}"


def OptionalVec2(v) -> Optional[Vec2]:
    if v is not None:
        return Vec2(v)
    else:
        return None


def sign_char(value: float) -> str:
    if value < 0.:
        return '-'
    elif value > 0:
        return '+'
    else:
        return ' '


def format_text(value: float, dimrnd: float = None, dimdec: int = None,
                dimzin: int = 0, dimdsep: str = '.',
                dimpost: str = '<>') -> str:
    if dimrnd is not None:
        value = xround(value, dimrnd)

    if dimdec is None:
        fmt = "{:f}"
        # Remove pending zeros for undefined decimal places:
        # '{:f}'.format(0) -> '0.000000'
        dimzin = dimzin | 8
    else:
        fmt = "{:." + str(dimdec) + "f}"
    text = fmt.format(value)

    leading = bool(dimzin & 4)
    pending = bool(dimzin & 8)
    text = suppress_zeros(text, leading, pending)
    if dimdsep != '.':
        text = text.replace('.', dimdsep)
    if dimpost:
        if '<>' in dimpost:
            fmt = dimpost.replace('<>', '{}', 1)
            text = fmt.format(text)
        else:
            raise DXFValueError(f'Invalid dimpost string: "{dimpost}"')
    return text


class BaseDimensionRenderer:
    """ Base rendering class for DIMENSION entities. """

    def __init__(self, dimension: 'Dimension', ucs: 'UCS' = None,
                 override: DimStyleOverride = None):
        self.doc: 'Drawing' = dimension.doc
        self.dimension: 'Dimension' = dimension
        self.dxfversion: str = self.doc.dxfversion
        self.supports_dxf_r2000: bool = self.dxfversion >= 'AC1015'
        self.supports_dxf_r2007: bool = self.dxfversion >= 'AC1021'
        # Target BLOCK of the graphical representation of the DIMENSION entity
        self.block: Optional['GenericLayoutType'] = None

        # DimStyleOverride object, manages dimension style overriding
        if override:
            self.dim_style = override
        else:
            self.dim_style = DimStyleOverride(dimension)

        # User defined coordinate system for DIMENSION entity
        self.ucs = ucs or PassTroughUCS()
        self.requires_extrusion: bool = not self.ucs.uz.isclose(Z_AXIS)

        # ezdxf specific attributes beyond DXF reference, therefore not stored
        # in the DXF file (DSTYLE).
        # Some of these are just an rendering effect, which will be ignored by
        # CAD applications if they modify the DIMENSION entity

        # User location override as UCS coordinates, stored as text_midpoint in
        # the DIMENSION entity
        self.user_location: Optional[Vec2] = OptionalVec2(
            self.dim_style.pop('user_location', None))

        # User location override relative to dimline center if True
        self.relative_user_location: bool = self.dim_style.pop(
            'relative_user_location', False)

        # Shift text away from default text location - implemented as user
        # location override without leader
        # Shift text along in text direction:
        self.text_shift_h: float = self.dim_style.pop('text_shift_h', 0.)
        # Shift text perpendicular to text direction:
        self.text_shift_v: float = self.dim_style.pop('text_shift_v', 0.)

        # Suppress arrow rendering - only rendering is suppressed (rendering
        # effect).
        # All placing related calculations are done without this settings.
        # Used for multi point linear dimensions to avoid double rendering of
        # non arrow ticks.
        self.suppress_arrow1: bool = self.dim_style.pop(
            'suppress_arrow1', False)
        self.suppress_arrow2: bool = self.dim_style.pop(
            'suppress_arrow2', False)
        # End of ezdxf specific attributes

        # ---------------------------------------------
        # GENERAL PROPERTIES
        # ---------------------------------------------
        self.default_color: int = self.dimension.dxf.color  # ACI
        self.default_layer: str = self.dimension.dxf.layer

        # ezdxf locates attachment points always in the text center.
        # Fixed predefined value for ezdxf rendering:
        self.text_attachment_point: int = 5

        # Ignored by ezdxf:
        self.horizontal_direction: Optional[
            float] = self.dimension.get_dxf_attrib('horizontal_direction', None)

        get = self.dim_style.get
        # Overall scaling of DIMENSION entity:
        self.dim_scale: float = get('dimscale', 1)
        if self.dim_scale == 0:
            self.dim_scale = 1

        # Controls drawing of circle or arc center marks and center lines, for
        # DIMDIAMETER and DIMRADIUS, the center mark is drawn only if you place
        # the dimension line outside the circle or arc.
        # 0 = No center marks or lines are drawn
        # <0 = Center lines are drawn
        # >0 = Center marks are drawn
        self.dim_center_marks: int = get('dimcen', 0)

        # ---------------------------------------------
        # TEXT
        # ---------------------------------------------
        # Dimension measurement factor:
        self.dim_measurement_factor: float = get('dimlfac', 1)
        self.text_style_name: str = get('dimtxsty', self.default_text_style())

        self.text_style: 'Textstyle' = self.doc.styles.get(self.text_style_name)
        self.text_height: float = self.char_height * self.dim_scale
        self.text_width_factor: float = self.text_style.get_dxf_attrib(
            'width', 1.)
        # text_gap: gap between dimension line an dimension text
        self.text_gap: float = get('dimgap', 0.625) * self.dim_scale
        # User defined text rotation - overrides everything:
        self.user_text_rotation: float = self.dimension.get_dxf_attrib(
            'text_rotation', None)
        # calculated text rotation
        self.text_rotation: float = self.user_text_rotation
        self.text_color: int = get('dimclrt', self.default_color)  # ACI
        self.text_round: Optional[float] = get('dimrnd', None)
        self.text_decimal_places: Optional[int] = get('dimdec', None)

        # Controls the suppression of zeros in the primary unit value.
        # Values 0-3 affect feet-and-inch dimensions only and are not supported
        # 4 (Bit 3) = Suppresses leading zeros in decimal dimensions,
        #   e.g. 0.5000 becomes .5000
        # 8 (Bit 4) = Suppresses trailing zeros in decimal dimensions,
        #   e.g. 12.5000 becomes 12.5
        # 12 (Bit 3+4) = Suppresses both leading and trailing zeros,
        #   e.g. 0.5000 becomes .5)
        self.text_suppress_zeros: int = get('dimzin', 0)

        dimdsep: int = self.dim_style.get('dimdsep', 0)
        self.text_decimal_separator: str = ',' if dimdsep == 0 else chr(dimdsep)

        self.text_format: str = self.dim_style.get('dimpost', '<>')
        # text_fill:
        # 0 = None
        # 1 = Background
        # 2 = DIMTFILLCLR
        self.text_fill: int = self.dim_style.get('dimtfill', 0)
        self.text_fill_color: int = self.dim_style.get('dimtfillclr', 1)  # ACI
        self.text_box_fill_scale = 1.1

        # text_halign:
        # 0 = center
        # 1 = left
        # 2 = right
        # 3 = above ext1
        # 4 = above ext2
        self.text_halign: int = get('dimjust', 0)

        # text_valign:
        # 0 = center
        # 1 = above
        # 2 = farthest away?
        # 3 = JIS;
        # 4 = below
        # Options 2, 3 are ignored by ezdxf
        self.text_valign: int = get('dimtad', 0)

        # Controls the vertical position of dimension text above or below the
        # dimension line, when DIMTAD = 0.
        # The magnitude of the vertical offset of text is the product of the
        # text height (+gap?) and DIMTVP.
        # Setting DIMTVP to 1.0 is equivalent to setting DIMTAD = 1.
        self.text_vertical_position: float = get('dimtvp', 0.)

        # Move text freely:
        self.text_movement_rule: int = get('dimtmove', 2)

        self.text_has_leader: bool = (self.user_location is not None
                                      and self.text_movement_rule == 1)

        # text_rotation is 0 if dimension text is 'inside', ezdxf defines
        # 'inside' as at the default text location:
        self.text_inside_horizontal: int = get('dimtih', 0)

        # text_rotation is 0 if dimension text is 'outside', ezdxf defines
        # 'outside' as NOT at the default text location:
        self.text_outside_horizontal: int = get('dimtoh', 0)

        # Force text location 'inside', even if the text should be moved
        # 'outside':
        self.force_text_inside: int = bool(get('dimtix', 0))

        # How dimension text and arrows are arranged when space is not
        # sufficient to place both 'inside':
        # 0 = Places both text and arrows outside extension lines
        # 1 = Moves arrows first, then text
        # 2 = Moves text first, then arrows
        # 3 = Moves either text or arrows, whichever fits best
        # not supported - ezdxf behaves like 2
        self.text_fitting_rule: int = get('dimatfit', 2)

        # Units for all dimension types except Angular.
        # 1 = Scientific
        # 2 = Decimal
        # 3 = Engineering
        # 4 = Architectural (always displayed stacked)
        # 5 = Fractional (always displayed stacked)
        # not supported - ezdxf behaves like 2
        self.text_length_unit: int = get('dimlunit', 2)

        # Fraction format when DIMLUNIT is set to 4 (Architectural) or
        # 5 (Fractional).
        # 0 = Horizontal stacking
        # 1 = Diagonal stacking
        # 2 = Not stacked (for example, 1/2)
        self.text_fraction_format: int = get('dimfrac', 0)  # not supported

        # Units format for angular dimensions
        # 0 = Decimal degrees
        # 1 = Degrees/minutes/seconds (not supported) same as 0
        # 2 = Grad
        # 3 = Radians
        self.text_angle_unit: int = get('dimaunit', 0)

        # Text_outside is only True if really placed outside of default text
        # location
        # remark: user defined text location is always outside per definition
        # (not by real location)
        self.text_outside: bool = False

        # Calculated or overridden dimension text location
        self.text_location: Optional[Vec2] = None

        # Bounding box of dimension text including border space
        self.text_box: Optional[TextBox] = None

        # Formatted dimension text
        self.text: str = ""

        # True if dimension text doesn't fit between extension lines
        self.is_wide_text: bool = False

        # ---------------------------------------------
        # ARROWS & TICKS
        # ---------------------------------------------
        self.tick_size: float = get('dimtsz', 0) * self.dim_scale
        self.arrow1_name: Optional[str] = None
        self.arrow2_name: Optional[str] = None
        self.arrow_size: float = 0.25

        if self.tick_size > 0:
            # Use oblique strokes as 'arrows', disables usual 'arrows' and user
            # defined blocks tick size is per definition double the size of
            # arrow size adjust arrow size to reuse the 'oblique' arrow block
            self.arrow_size = self.tick_size * 2
        else:
            # Arrow name or block name if user defined arrow
            self.arrow1_name, self.arrow2_name = self.dim_style.get_arrow_names()
            self.arrow_size = get('dimasz', 0.25) * self.dim_scale

        # Suppresses arrowheads if not enough space is available inside the
        # extension lines.
        # Only if force_text_inside is True
        self.suppress_arrow_heads: int = get('dimsoxd', 0)  # not supported yet

        # ---------------------------------------------
        # DIMENSION LINE
        # ---------------------------------------------
        self.dim_line_color: int = get('dimclrd', self.default_color)

        # Dimension line extension, along the dimension line direction ('left'
        # and 'right')
        self.dim_line_extension: float = get('dimdle', 0.) * self.dim_scale
        self.dim_linetype: Optional[str] = get('dimltype', None)
        self.dim_lineweight: int = get('dimlwd', const.LINEWEIGHT_BYBLOCK)

        # Suppress first part of the dimension line
        self.suppress_dim1_line: int = get('dimsd1', 0)

        # Suppress second part of the dimension line
        self.suppress_dim2_line: int = get('dimsd2', 0)

        # Controls whether a dimension line is drawn between the extension lines
        # even when the text is placed outside.
        # For radius and diameter dimensions (when DIMTIX is off), draws a
        # dimension line inside the circle or arc and places the text,
        # arrowheads, and leader outside.
        # 0 = no dimension line
        # 1 = draw dimension line
        # not supported yet - ezdxf behaves like option 1
        self.dim_line_if_text_outside: int = get('dimtofl', 1)

        # ---------------------------------------------
        # EXTENSION LINES
        # ---------------------------------------------
        self.ext_line_color: int = get('dimclre', self.default_color)
        self.ext1_linetype_name: Optional[str] = get('dimltex1', None)
        self.ext2_linetype_name: Optional[str] = get('dimltex2', None)
        self.ext_lineweight: int = get('dimlwe', const.LINEWEIGHT_BYBLOCK)
        self.suppress_ext1_line: int = get('dimse1', 0)
        self.suppress_ext2_line: int = get('dimse2', 0)

        # Extension of extension line above the dimension line, in extension
        # line direction in most cases perpendicular to dimension line
        # (oblique!)
        self.ext_line_extension: float = get('dimexe', 0.) * self.dim_scale

        # Distance of extension line from the measurement point in extension
        # line direction
        self.ext_line_offset: float = get('dimexo', 0.) * self.dim_scale

        # Fixed length extension line, leenght above dimension line is still
        # self.ext_line_extension
        self.ext_line_fixed: int = get('dimfxlon', 0)

        # Length below the dimension line:
        self.ext_line_length: float = get(
            'dimfxl', self.ext_line_extension) * self.dim_scale

        # ---------------------------------------------
        # TOLERANCES & LIMITS
        # ---------------------------------------------
        # Appends tolerances to dimension text. Setting DIMTOL to on turns
        # DIMLIM off.
        self.dim_tolerance: int = get('dimtol', 0)
        # Generates dimension limits as the default text. Setting DIMLIM to On
        # turns DIMTOL off.
        self.dim_limits: int = get('dimlim', 0)

        if self.dim_tolerance:
            self.dim_limits = 0

        if self.dim_limits:
            self.dim_tolerance = 0

        # Scale factor for the text height of fractions and tolerance values
        # relative to the dimension text height
        self.tol_text_scale_factor = get('dimtfac', .5)

        # Default MTEXT line spacing for tolerances (BricsCAD)
        self.tol_line_spacing = 1.35

        # Sets the minimum (or lower) tolerance limit for dimension text when
        # DIMTOL or DIMLIM is on.
        # DIMTM accepts signed values.
        # If DIMTOL is on and DIMTP and DIMTM are set to the same value, a
        # tolerance value is drawn.
        # If DIMTM and DIMTP values differ, the upper tolerance is drawn above
        # the lower, and a plus sign is added to the DIMTP value if it is
        # positive.
        # For DIMTM, the program uses the negative of the value you enter
        # (adding a minus sign if you specify a positive number and a plus sign
        # if you specify a negative number).
        self.tol_minimum: float = get('dimtm', 0)

        # Sets the maximum (or upper) tolerance limit for dimension text when
        # DIMTOL or DIMLIM is on.
        # DIMTP accepts signed values.
        # If DIMTOL is on and DIMTP and DIMTM are set to the same value, a
        # tolerance value is drawn.
        # If DIMTM and DIMTP values differ, the upper tolerance is drawn above
        # the lower and a plus sign is added to the DIMTP value if it is
        # positive.
        self.tol_maximum: float = get('dimtp', 0)

        # Number of decimal places to display in tolerance values
        self.tol_decimal_places: int = get('dimtdec', 4)

        # Vertical justification for tolerance values relative to the nominal dimension text
        # 0 = Bottom
        # 1 = Middle
        # 2 = Top
        self.tol_valign: int = get('dimtolj', 0)

        # Same as DIMZIN for tolerances (self.text_suppress_zeros)
        self.tol_suppress_zeros: int = get('dimtzin', 0)
        self.tol_text: Optional[str] = None
        self.tol_text_height: float = 0
        self.tol_text_upper: Optional[str] = None
        self.tol_text_lower: Optional[str] = None
        self.tol_char_height: float = (
                self.char_height * self.tol_text_scale_factor * self.dim_scale
        )
        # Tolerances
        if self.dim_tolerance:
            # Single tolerance value +/- value
            if self.tol_minimum == self.tol_maximum:
                self.tol_text = PLUS_MINUS + self.format_tolerance_text(
                    abs(self.tol_maximum))
                self.tol_text_height = self.tol_char_height
                self.tol_text_width = self.tolerance_text_width(
                    len(self.tol_text))
            else:  # 2 stacked values: +upper tolerance <above> -lower tolerance
                self.tol_text_upper = sign_char(
                    self.tol_maximum) + self.format_tolerance_text(
                    abs(self.tol_maximum))
                self.tol_text_lower = sign_char(
                    self.tol_minimum * -1) + self.format_tolerance_text(
                    abs(self.tol_minimum))
                # requires 2 text lines
                self.tol_text_height = self.tol_char_height + (
                        self.tol_text_height * self.tol_line_spacing)
                self.tol_text_width = self.tolerance_text_width(
                    max(len(self.tol_text_upper), len(self.tol_text_lower)))
            # Reset text height
            self.text_height = max(self.text_height, self.tol_text_height)

        elif self.dim_limits:
            # Always None for limits:
            self.tol_text = None
            # Limits text is always 2 stacked numbers and requires actual
            # measurement:
            self.tol_text_upper = None  # text for upper limit
            self.tol_text_lower = None  # text for lower limit
            self.tol_text_height = self.tol_char_height + (
                    self.tol_text_height * self.tol_line_spacing)
            self.tol_text_width = None  # requires actual measurement
            self.text_height = max(self.text_height, self.tol_text_height)

    def default_text_style(self):
        style = options.default_dimension_text_style
        if style not in self.doc.styles:
            style = 'Standard'
        return style

    @property
    def text_inside(self):
        return not self.text_outside

    def render(self, block: 'GenericLayoutType'):
        # Block entities are located in the OCS defined by the extrusion vector
        # of the DIMENSION entity and the z-axis of the OCS point
        # 'text_midpoint' (group code 11).
        self.block = block
        # Tolerance requires MTEXT support, switch off rendering of tolerances
        # and limits
        if not self.supports_dxf_r2000:
            self.dim_tolerance = 0
            self.dim_limits = 0

    @property
    def char_height(self) -> float:
        """ Unscaled (self.dim_scale) character height defined by text style or
        DIMTXT. Hint: Use self.text_height for proper scaled text height in
        drawing units.

        """
        height: float = self.text_style.get_dxf_attrib('height', 0)
        if height == 0:  # variable text height (not fixed)
            height = self.dim_style.get('dimtxt', 1.)
        return height

    def text_width(self, text: str) -> float:
        """
        Return width of `text` in drawing units.

        """
        char_width = self.text_height * self.text_width_factor
        return len(text) * char_width

    def tolerance_text_width(self, count: int) -> float:
        """ Return width of `count` characters in drawing units. """
        return self.tol_text_height * self.text_width_factor * count

    def default_attributes(self) -> dict:
        """ Returns default DXF attributes as dict. """
        return {
            'layer': self.default_layer,
            'color': self.default_color,
        }

    def dim_line_attributes(self) -> dict:
        """ Returns default dimension line DXF attributes as dict. """
        attribs = {
            'color': self.dim_line_color
        }
        if self.dim_linetype is not None:
            attribs['linetype'] = self.dim_linetype

        if self.supports_dxf_r2000:
            attribs['lineweight'] = self.dim_lineweight
        return attribs

    def text_override(self, measurement: float) -> str:
        """ Create dimension text for `measurement` in drawing units and applies
        text overriding properties.

        """
        text = self.dimension.dxf.text
        if text == ' ':  # suppress text
            return ''
        elif text == '' or text == '<>':  # measured distance
            return self.format_text(measurement)
        else:  # user override
            return text

    def format_text(self, value: float) -> str:
        """ Rounding and text formatting of `value`, removes leading and
        trailing zeros if necessary.

        """
        return format_text(
            value,
            self.text_round,
            self.text_decimal_places,
            self.text_suppress_zeros,
            self.text_decimal_separator,
            self.text_format,
        )

    def compile_mtext(self) -> str:
        text = self.text
        if self.dim_tolerance:
            align = max(int(self.tol_valign), 0)
            align = min(align, 2)
            if self.tol_text is None:
                text = TOLERANCE_TEMPLATE2.format(
                    align=align,
                    txt=text,
                    fac=self.tol_text_scale_factor,
                    upr=self.tol_text_upper,
                    lwr=self.tol_text_lower,
                )
            else:
                text = TOLERANCE_TEMPLATE1.format(
                    align=align,
                    txt=text,
                    fac=self.tol_text_scale_factor,
                    tol=self.tol_text,
                )
        elif self.dim_limits:
            text = LIMITS_TEMPLATE.format(
                upr=self.tol_text_upper,
                lwr=self.tol_text_lower,
                fac=self.tol_text_scale_factor,
            )
        return text

    def format_tolerance_text(self, value: float) -> str:
        """ Rounding and text formatting of tolerance `value`, removes leading
        and trailing zeros if necessary.

        """
        return format_text(
            value=value,
            dimrnd=None,
            dimdec=self.tol_decimal_places,
            dimzin=self.tol_suppress_zeros,
            dimdsep=self.text_decimal_separator,
        )

    def location_override(self, location: 'Vertex', leader=False,
                          relative=False) -> None:
        """ Set user defined dimension text location. ezdxf defines a user
        defined location per definition as 'outside'.

        Args:
            location: text midpoint
            leader: use leader or not (movement rules)
            relative: is location absolute (in UCS) or relative to dimension
                line center.

        """
        self.dim_style.set_location(location, leader, relative)
        self.user_location = Vec2(location)
        self.text_movement_rule = 1 if leader else 2
        self.relative_user_location = relative
        self.text_outside = True

    def add_line(self, start: 'Vertex', end: 'Vertex', dxfattribs: dict = None,
                 remove_hidden_lines=False) -> None:
        """ Add a LINE entity to the dimension BLOCK. Removes parts of the line
        hidden by dimension text if `remove_hidden_lines` is True.

        Args:
            start: start point of line
            end: end point of line
            dxfattribs: additional or overridden DXF attributes
            remove_hidden_lines: removes parts of the line hidden by dimension
                text if ``True``

        """

        def add_line_to_block(start, end):
            self.block.add_line(to_ocs(Vec3(start)).vec2,
                                to_ocs(Vec3(end)).vec2,
                                dxfattribs=dxfattribs)

        def order(a: Vec2, b: Vec2) -> Tuple[Vec2, Vec2]:
            if (start - a).magnitude < (start - b).magnitude:
                return a, b
            else:
                return b, a

        to_ocs = self.ucs.to_ocs
        attribs = self.default_attributes()
        if dxfattribs:
            attribs.update(dxfattribs)
        text_box = self.text_box
        if remove_hidden_lines and (text_box is not None):
            start_inside = int(text_box.is_inside(start))
            end_inside = int(text_box.is_inside(end))
            inside = start_inside + end_inside
            if inside == 2:  # start and end inside text_box
                return  # do not draw line
            elif inside == 1:  # one point inside text_box or on a border line
                intersection_points = text_box.intersect(
                    ConstructionLine(start, end))
                if len(intersection_points) == 1:
                    # one point inside one point outside -> one intersection point
                    p1 = intersection_points[0]
                else:
                    # second point on a text box border line
                    p1, _ = order(*intersection_points)
                p2 = start if end_inside else end
                add_line_to_block(p1, p2)
                return
            else:
                intersection_points = text_box.intersect(
                    ConstructionLine(start, end))
                if len(intersection_points) == 2:
                    # sort intersection points by distance to start point
                    p1, p2 = order(intersection_points[0],
                                   intersection_points[1])
                    # line[start-p1] - gap - line[p2-end]
                    add_line_to_block(start, p1)
                    add_line_to_block(p2, end)
                    return
                # else: fall trough
        add_line_to_block(start, end)

    def add_blockref(self, name: str, insert: 'Vertex', rotation: float = 0,
                     scale: float = 1., dxfattribs: dict = None) -> None:
        """
        Add block references and standard arrows to the dimension BLOCK.

        Args:
            name: block or arrow name
            insert: insertion point in UCS
            rotation: rotation angle in degrees in UCS (x-axis is 0 degrees)
            scale: scaling factor for x- and y-direction
            dxfattribs: additional or overridden DXF attributes

        """
        insert = self.ucs.to_ocs(Vec3(insert)).vec2
        rotation = self.ucs.to_ocs_angle_deg(rotation)

        attribs = self.default_attributes()
        # Generates automatically BLOCK definitions for arrows if needed:
        if name in ARROWS:
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_arrow_blockref(name, insert=insert, size=scale,
                                          rotation=rotation, dxfattribs=attribs)
        else:
            if name is None or name not in self.doc.blocks:
                raise DXFUndefinedBlockError(f'Undefined block: "{name}"')
            attribs['rotation'] = rotation
            if scale != 1.:
                attribs['xscale'] = scale
                attribs['yscale'] = scale
            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_blockref(name, insert=insert, dxfattribs=attribs)

    def add_text(self, text: str, pos: Vec3, rotation: float,
                 dxfattribs: dict = None) -> None:
        """
        Add TEXT (DXF R12) or MTEXT (DXF R2000+) entity to the dimension BLOCK.

        Args:
            text: text as string
            pos: insertion location in UCS
            rotation: rotation angle in degrees in UCS (x-axis is 0 degrees)
            dxfattribs: additional or overridden DXF attributes

        """
        pos = self.ucs.to_ocs(pos).vec2
        rotation = self.ucs.to_ocs_angle_deg(rotation)

        attribs = self.default_attributes()
        attribs['style'] = self.text_style_name
        attribs['color'] = self.text_color

        if self.supports_dxf_r2000:
            attribs['text_direction'] = Vec2.from_deg_angle(rotation)
            attribs['char_height'] = self.text_height
            attribs['insert'] = pos
            attribs['attachment_point'] = self.text_attachment_point

            if self.supports_dxf_r2007:
                if self.text_fill:
                    attribs['box_fill_scale'] = self.text_box_fill_scale
                    attribs['bg_fill_color'] = self.text_fill_color
                    attribs['bg_fill'] = 3 if self.text_fill == 1 else 1

            if dxfattribs:
                attribs.update(dxfattribs)
            self.block.add_mtext(text, dxfattribs=attribs)
        else:
            attribs['rotation'] = rotation
            attribs['height'] = self.text_height
            if dxfattribs:
                attribs.update(dxfattribs)
            dxftext = self.block.add_text(text, dxfattribs=attribs)
            dxftext.set_pos(pos, align='MIDDLE_CENTER')

    def add_defpoints(self, points: Iterable['Vertex']) -> None:
        """
        Add POINT entities at layer 'DEFPOINTS' for all points in `points`.

        """
        attribs = {
            'layer': 'DEFPOINTS',
        }
        for point in points:
            location = self.ucs.to_ocs(Vec3(point)).replace(z=0)
            self.block.add_point(location, dxfattribs=attribs)

    def add_leader(self, p1: Vec2, p2: Vec2, p3: Vec2, dxfattribs: dict = None):
        """
        Add simple leader line from p1 to p2 to p3.

        Args:
            p1: target point
            p2: first text point
            p3: second text point
            dxfattribs: DXF attribute

        """
        self.add_line(p1, p2, dxfattribs)
        self.add_line(p2, p3, dxfattribs)

    def transform_ucs_to_wcs(self) -> None:
        pass  # abstract method

    @property
    def vertical_placement(self) -> float:
        """ Returns vertical placement of dimension text as 1 for above, 0 for
        center and -1 for below dimension line.

        """
        if self.text_valign == 0:
            return 0
        elif self.text_valign == 4:
            return -1
        else:
            return 1

    def text_vertical_distance(self) -> float:
        """ Returns the vertical distance for dimension line to text midpoint.
        Positive values are above the line, negative values are below the line.

        """
        if self.text_valign == 0:
            return self.text_height * self.text_vertical_position
        else:
            return (
                           self.text_height / 2. + self.text_gap) * self.vertical_placement

    def finalize(self) -> None:
        self.transform_ucs_to_wcs()


def order_leader_points(p1: Vec2, p2: Vec2, p3: Vec2) -> Tuple[Vec2, Vec2]:
    if (p1 - p2).magnitude > (p1 - p3).magnitude:
        return p3, p2
    else:
        return p2, p3
