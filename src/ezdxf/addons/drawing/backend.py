# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Iterable, List, Dict

from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.entities import DXFGraphic
from ezdxf.tools.text import replace_non_printable_characters
from ezdxf.math import Vec3, Matrix44
from ezdxf.path import Path

if TYPE_CHECKING:
    from ezdxf.tools.fonts import FontFace, FontMeasurements

# Some params are also used by the Frontend() which has access to the backend
# attributes:
# show_defpoints: frontend filters defpoints if option is 0
# show_hatch: frontend filters all HATCH entities if option is 0
DEFAULT_PARAMS = {
    # Updated by Frontend() class, if not set by user:
    "pdsize": None,
    # 0   5% of draw area height
    # <0  Specifies a percentage of the viewport size
    # >0  Specifies an absolute size

    # See POINT docs:
    "pdmode": None,

    # Do not show defpoints by default.
    # Filtering is handled by the Frontend().
    "show_defpoints": 0,

    # linetype render:
    # "internal" or "ezdxf"
    "linetype_renderer": "internal",

    # overall linetype scaling: None as default is important!
    # 0.0 = disable line types at all, only supported by PyQt backend yet!
    "linetype_scaling": 1.0,

    # lineweight_scaling: 0.0 to disable lineweights at all - the current
    # result is correct, in SVG the line width is 0.7 points for 0.25mm as
    # required, but it often looks too thick
    "lineweight_scaling": 1.0,
    "min_lineweight": 0.24,  # 1/300 inch
    "min_dash_length": 0.1,  # just guessing
    "max_flattening_distance": 0.01,  # just guessing

    # 0 = disable HATCH entities
    # 1 = show HATCH entities
    # Filtering is  handled by the Frontend().
    "show_hatch": 1,

    # 0 = disable hatch pattern
    # 1 = use predefined matplotlib pattern by pattern-name matching
    # 2 = draw as solid fillings
    "hatch_pattern": 1,
}


class Backend(ABC):
    def __init__(self, params: Dict = None):
        params_ = dict(DEFAULT_PARAMS)
        if params:
            err = set(params.keys()) - set(DEFAULT_PARAMS.keys())
            if err:
                raise ValueError(f'Invalid parameter(s): {str(err)}')
            params_.update(params)
        self.entity_stack: List[Tuple[DXFGraphic, Properties]] = []
        self.pdsize = params_['pdsize']
        self.pdmode = params_['pdmode']
        self.show_defpoints = params_['show_defpoints']
        self.show_hatch = params_['show_hatch']
        self.hatch_pattern = params_['hatch_pattern']
        self.linetype_renderer = params_['linetype_renderer'].lower()
        self.linetype_scaling = params_['linetype_scaling']
        self.lineweight_scaling = params_['lineweight_scaling']
        self.min_lineweight = params_['min_lineweight']
        self.min_dash_length = params_['min_dash_length']

        # Real document measurement value will be updated by the Frontend():
        # 0=Imperial (in, ft, yd, ...); 1=ISO meters
        self.measurement = 0

        # Deprecated: instead use Path.flattening() for approximation
        self.bezier_approximation_count: int = 32

        # Max flattening distance in drawing units: the backend implementation
        # should calculate an appropriate value, like 1 screen- or paper pixel
        # on the output medium, but converted into drawing units.
        # Set Path() approximation accuracy:
        self.max_flattening_distance = params_['max_flattening_distance']

    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        self.entity_stack.append((entity, properties))

    def exit_entity(self, entity: DXFGraphic) -> None:
        e, p = self.entity_stack.pop()
        assert e is entity, 'entity stack mismatch'

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """ Obtain the current entity being drawn """
        return self.entity_stack[-1][0] if self.entity_stack else None

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        """ Draw a real dimensionless point, because not all backends support
        zero-length lines!
        """
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vec3, end: Vec3,
                  properties: Properties) -> None:
        raise NotImplementedError

    def draw_path(self, path: Path, properties: Properties) -> None:
        """ Draw an outline path (connected string of line segments and Bezier
        curves).

        The :meth:`draw_path` implementation is a fall-back implementation
        which approximates Bezier curves by flattening as line segments.
        Backends can override this method if better path drawing functionality
        is available for that backend.

        """
        if len(path):
            vertices = iter(
                path.flattening(distance=self.max_flattening_distance)
            )
            prev = next(vertices)
            for vertex in vertices:
                self.draw_line(prev, vertex, properties)
                prev = vertex

    def draw_filled_paths(self, paths: Iterable[Path], holes: Iterable[Path],
                          properties: Properties) -> None:
        """ Draw multiple filled paths (connected string of line segments and
        Bezier curves) with holes.

        The strategy to draw multiple paths at once was chosen, because a HATCH
        entity can contain multiple unconnected areas and the holes are not easy
        to assign to an external path.

        The idea is to put all filled areas into `paths` (counter-clockwise
        winding) and all holes into `holes` (clockwise winding) and look what
        the backend does with this information.

        The HATCH fill strategies ("ignore", "outermost", "ignore") are resolved
        by the frontend e.g. the holes sequence is empty for the "ignore"
        strategy and for the "outermost" strategy, holes do not contain nested
        holes.

        The default implementation draws all paths as filled polygon without
        holes by the :meth:`draw_filled_polygon` method. Backends can override
        this method if filled polygon with hole support is available.

        Args:
            paths: sequence of exterior paths (counter-clockwise winding)
            holes: sequence of holes (clockwise winding)
            properties: HATCH properties

        """
        for path in paths:
            self.draw_filled_polygon(
                path.flattening(distance=self.max_flattening_distance),
                properties
            )

    @abstractmethod
    def draw_filled_polygon(self, points: Iterable[Vec3],
                            properties: Properties) -> None:
        """ Fill a polygon whose outline is defined by the given points.
        Used to draw entities with simple outlines where :meth:`draw_path` may
        be an inefficient way to draw such a polygon.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, text: str, transform: Matrix44, properties: Properties,
                  cap_height: float) -> None:
        """ Draw a single line of text with the anchor point at the baseline
        left point.
        """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(self, cap_height: float,
                              font: 'FontFace' = None) -> 'FontMeasurements':
        """ Note: backends might want to cache the results of these calls """
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(self, text: str, cap_height: float,
                            font: 'FontFace' = None) -> float:
        """ Get the width of a single line of text. """
        # https://stackoverflow.com/questions/32555015/how-to-get-the-visual-length-of-a-text-string-in-python
        # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """ Clear the canvas. Does not reset the internal state of the backend.
        Make sure that the previous drawing is finished before clearing.

        """
        raise NotImplementedError

    def finalize(self) -> None:
        pass


def prepare_string_for_rendering(text: str, dxftype: str) -> str:
    assert '\n' not in text, 'not a single line of text'
    if dxftype in {'TEXT', 'ATTRIB', 'ATTDEF'}:
        text = replace_non_printable_characters(text, replacement='?')
        text = text.replace('\t', '?')
    elif dxftype == 'MTEXT':
        text = replace_non_printable_characters(text, replacement='▯')
        text = text.replace('\t', '        ')
    else:
        raise TypeError(dxftype)
    return text
