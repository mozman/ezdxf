# Created: 17.05.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
"""
Translate DXF entities and structures into Python source code.

"""
from typing import TYPE_CHECKING, Iterable, List, TextIO, Mapping, Set
import json

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Insert, MText, LWPolyline, Polyline, Spline, Leader, Dimension, Image
    from ezdxf.eztypes import Mesh, Hatch

__all__ = ['entities_to_code']


def entities_to_code(entities: Iterable['DXFGraphic'], layout: str = 'layout') -> 'SourceCodeGenerator':
    """
    Translates DXF entities into Python source code for creating the same DXF entities in another
    model space or block definition.

    Args:
        entities: iterable of DXFGraphic
        layout: variable name of the layout (model space or block)

    Returns: :class:`SourceCodeGenerator`

    """
    code_generator = SourceCodeGenerator(layout=layout)
    code_generator.translate_entities(entities)
    return code_generator


PURGE_DXF_ATTRIBUTES = {'handle', 'owner', 'paperspace', 'material_handle', 'visualstyle_handle', 'plotstyle_handle'}


def purge_dxf_attributes(attribs: dict) -> dict:
    """
    Purge DXF attributes which will be invalid in a new document (handles), or which will be set automatically by
    adding an entity to a layout (paperspace).

    Args:
        attribs: entity DXF attributes dictionary

    """
    return {k: v for k, v in attribs.items() if k not in PURGE_DXF_ATTRIBUTES}


def fmt_mapping(mapping: Mapping, indent: int = 0) -> Iterable[str]:
    # key is always a string
    fmt = ' ' * indent + "'{}': {},"
    for k, v in mapping.items():
        assert isinstance(k, str)
        if isinstance(v, str):
            v = json.dumps(v)  # for correct escaping of quotes
        else:
            v = str(v)  # format uses repr() for Vectors
        yield fmt.format(k, v)


def fmt_list(l: Iterable, indent: int = 0) -> Iterable[str]:
    fmt = ' ' * indent + '{},'
    for v in l:
        yield (fmt.format(str(v)))


class SourceCodeGenerator:
    """
    The SourceCodeGenerator translates DXF entities into Python source code for creating the same DXF entity in another
    model space or block definition.

    Args:
        layout: variable name of the layout (model space or block)

    """

    def __init__(self, layout: str = 'layout'):
        self.layout = layout
        self.source_code = []  # type: List[str]
        self.used_layers = set()  # type: Set[str]  # layer names as string
        self.used_styles = set()  # type: Set[str]  # text style name as string, requires a TABLE entry
        self.used_linetypes = set()  # type: Set[str]  # line type names as string, requires a TABLE entry
        self.used_dimstyles = set()  # type: Set[str]  # dimension style names as string, requires a TABLE entry
        self.used_blocks = set()  # type: Set[str]  # block names as string, requires a BLOCK definition

    def translate_entity(self, entity: 'DXFGraphic') -> None:
        dxftype = entity.dxftype()
        try:
            entity_translator = getattr(self, '_' + dxftype.lower())
        except AttributeError:
            self.add_source_code_line('# unsupported DXF entity "{}"'.format(dxftype))
        else:
            entity_translator(entity)

    def translate_entities(self, entities: Iterable['DXFGraphic']) -> None:
        for entity in entities:
            self.translate_entity(entity)

    def add_used_resources(self, dxfattribs: Mapping) -> None:
        if 'layer' in dxfattribs:
            self.used_layers.add(dxfattribs['layer'])
        if 'linetype' in dxfattribs:
            self.used_linetypes.add(dxfattribs['linetype'])
        if 'style' in dxfattribs:
            self.used_styles.add(dxfattribs['style'])
        if 'dimstyle' in dxfattribs:
            self.used_dimstyles.add(dxfattribs['dimstyle'])

    def add_source_code_line(self, code: str) -> None:
        self.source_code.append(code)

    def add_source_code_lines(self, code: Iterable[str]) -> None:
        self.source_code.extend(code)

    def add_list_source_code(self, values: Iterable, prolog: str = '[', epilog: str = ']', indent: int = 0) -> None:
        fmt_str = ' ' * indent + '{}'
        self.add_source_code_line(fmt_str.format(prolog))
        self.add_source_code_lines(fmt_list(values, indent=4 + indent))
        self.add_source_code_line(fmt_str.format(epilog))

    def add_dict_source_code(self, mapping: Mapping, prolog: str = '{', epilog: str = '}', indent: int = 0) -> None:
        fmt_str = ' ' * indent + '{}'
        self.add_source_code_line(fmt_str.format(prolog))
        self.add_source_code_lines(fmt_mapping(mapping, indent=4 + indent))
        self.add_source_code_line(fmt_str.format(epilog))

    def entity_source_code(self, dxftype: str, dxfattribs: dict, prefix: str = '') -> Iterable[str]:
        """
        Returns the source code string to create a DXF entity.

        Args:
            dxftype: DXF entity type as string, like 'LINE'
            dxfattribs: DXF attributes dictionary
            prefix: prefix string like a variable assigment 'e = '

        """
        dxfattribs = purge_dxf_attributes(dxfattribs)
        self.add_used_resources(dxfattribs)
        s = [
            prefix + "{}.new_entity(".format(self.layout),
            "    '{}',".format(dxftype),
            "     dxfattribs={"
        ]
        s.extend(fmt_mapping(dxfattribs, indent=8))
        s.extend([
            "    },",
            ")",
        ])
        return s

    def tostring(self, indent: int = 0) -> str:
        lead_str = ' ' * indent
        return '\n'.join(lead_str + line for line in self.source_code)

    def __str__(self) -> str:
        return self.tostring()

    def writelines(self, stream: TextIO, indent: int = 0):
        fmt = ' ' * indent + '{}\n'
        for line in self.source_code:
            stream.write(fmt.format(line))

    # simple types

    def _line(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('LINE', entity.dxfattribs()))

    def _point(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('POINT', entity.dxfattribs()))

    def _circle(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('CIRCLE', entity.dxfattribs()))

    def _arc(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('ARC', entity.dxfattribs()))

    def _text(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('TEXT', entity.dxfattribs()))

    def _solid(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('SOLID', entity.dxfattribs()))

    def _trace(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('TRACE', entity.dxfattribs()))

    def _3dface(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('3DFACE', entity.dxfattribs()))

    def _shape(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('SHAPE', entity.dxfattribs()))

    def _attrib(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('ATTRIB', entity.dxfattribs()))

    def _attdef(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('ATTDEF', entity.dxfattribs()))

    def _ellipse(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('ELLIPSE', entity.dxfattribs()))

    def _viewport(self, entity: 'DXFGraphic') -> None:
        self.add_source_code_lines(self.entity_source_code('VIEWPORT', entity.dxfattribs()))
        self.add_source_code_line(
            '# Set valid handles or remove attributes ending with "_handle", else the DXF file is invalid for AutoCAD')

    # complex types

    def _insert(self, entity: 'Insert') -> None:
        self.used_blocks.add(entity.dxf.name)
        self.add_source_code_lines(self.entity_source_code('INSERT', entity.dxfattribs(), prefix='e = '))
        if len(entity.attribs):
            for attrib in entity.attribs:
                dxfattribs = attrib.dxfattribs()
                dxfattribs['layer'] = entity.dxf.layer  # set ATTRIB layer to same as INSERT
                self.add_source_code_lines(self.entity_source_code('ATTRIB', attrib.dxfattribs(), prefix='a = '))
                self.add_source_code_lines('e.attribs.append(a)')

    def _mtext(self, entity: 'MText') -> None:
        self.add_source_code_lines(self.entity_source_code('MTEXT', entity.dxfattribs(), prefix='e = '))
        # mtext content 'text' is not a single DXF tag and therefore not a DXF attribute
        self.add_source_code_line('e.text = {}'.format(json.dumps(entity.text)))

    def _lwpolyline(self, entity: 'LWPolyline') -> None:
        self.add_source_code_lines(self.entity_source_code('LWPOLYLINE', entity.dxfattribs(), prefix='e = '))
        # lwpolyline points are not DXF attributes
        self.add_list_source_code(entity.get_points(), prolog='e.set_points([', epilog='])')

    def _spline(self, entity: 'Spline') -> None:
        self.add_source_code_lines(self.entity_source_code('SPLINE', entity.dxfattribs(), prefix='e = '))
        # spline points, knots and weights are not DXF attributes
        if len(entity.fit_points):
            self.add_list_source_code(entity.fit_points, prolog='e.fit_points = [', epilog=']')

        if len(entity.control_points):
            self.add_list_source_code(entity.control_points, prolog='e.control_points = [', epilog=']')

        if len(entity.knots):
            self.add_list_source_code(entity.knots, prolog='e.knots = [', epilog=']')

        if len(entity.weights):
            self.add_list_source_code(entity.weights, prolog='e.weights = [', epilog=']')

    def _polyline(self, entity: 'Polyline') -> None:
        self.add_source_code_lines(self.entity_source_code('POLYLINE', entity.dxfattribs(), prefix='e = '))
        # polyline vertices are separate DXF entities and therefore not DXF attributes
        for v in entity.vertices:
            attribs = purge_dxf_attributes(v.dxfattribs())
            location = attribs.pop('location')
            if 'layer' in attribs:
                del attribs['layer']  # layer is automatically set to the POLYLINE layer

            # each VERTEX can have different DXF attributes: bulge, start_width, end_width ...
            self.add_source_code_line('e.append_vertex({}, dxfattribs={})'.format(
                str(location),
                attribs,
            ))

    def _leader(self, entity: 'Leader'):
        self.add_source_code_line('# Dimension style attribute overriding is not supported!')
        self.add_source_code_lines(self.entity_source_code('LEADER', entity.dxfattribs(), prefix='e = '))
        self.add_list_source_code(entity.vertices, prolog='e.set_vertices([', epilog='])')

    def _dimension(self, entity: 'Dimension'):
        self.add_source_code_line('# Dimension style attribute overriding is not supported!')
        self.add_source_code_lines(self.entity_source_code('DIMENSION', entity.dxfattribs(), prefix='e = '))
        self.add_source_code_lines([
            '# You have to create the required graphical representation for the DIMENSION entity as anonymous block, ',
            '# otherwise the DXF file is invalid for AutoCAD (but not for BricsCAD):',
            '# from ezdxf.dimstyleoverride import DimStyleOverride',
            '# DimStyleOverride(e).render()',
            ''
        ])

    def _image(self, entity: 'Image'):
        # remove handles which will be invalid in a new document
        self.add_source_code_line('# Image requires IMAGEDEF and IMAGEDEFREACTOR objects in the OBJECTS section!')
        self.add_source_code_lines(self.entity_source_code('IMAGE', entity.dxfattribs()))
        self.add_source_code_line(
            '# Set valid image_def_handle and image_def_reactor_handle, else the DXF file is invalid for AutoCAD')

    def _mesh(self, entity: 'Mesh'):
        def to_tuples(l):
            for e in l:
                yield tuple(e)

        self.add_source_code_lines(self.entity_source_code('MESH', entity.dxfattribs(), prefix='e = '))
        if len(entity.vertices):
            self.add_list_source_code(entity.vertices, prolog='e.vertices = [', epilog=']')
        if len(entity.edges):
            self.add_list_source_code(to_tuples(entity.edges), prolog='e.edges = [', epilog=']')
        if len(entity.faces):
            self.add_list_source_code(to_tuples(entity.faces), prolog='e.faces = [', epilog=']')
        if len(entity.creases):
            self.add_list_source_code(entity.creases, prolog='e.creases = [', epilog=']')

    def _hatch(self, entity: 'Hatch'):
        dxfattribs = entity.dxfattribs()
        dxfattribs['associative'] = 0  # associative hatch not supported
        self.add_source_code_lines(self.entity_source_code('HATCH', dxfattribs, prefix='e = '))
        if len(entity.seeds):
            self.add_source_code_line("e.set_seed_points({})".format(str(entity.seeds)))
        if entity.pattern:
            self.add_source_code_line('e.set_pattern_definition([')
            for line in entity.pattern.lines:
                self.add_source_code_line('    {},'.format(str(line)))
            self.add_source_code_line('])')
        arg = "    '{}'={},"
        if entity.has_gradient_data:
            g = entity.gradient
            self.add_source_code_line('e.set_gradient(')
            self.add_source_code_line(arg.format('color1', str(g.color1)))
            self.add_source_code_line(arg.format('color2', str(g.color2)))
            self.add_source_code_line(arg.format('rotation', g.rotation))
            self.add_source_code_line(arg.format('centered', g.centered))
            self.add_source_code_line(arg.format('one_color', g.one_color))
            self.add_source_code_line(arg.format('name', json.dumps(g.name)))
            self.add_source_code_line(')')
        for count, path in enumerate(entity.paths, start=1):
            if path.PATH_TYPE == 'PolylinePath':
                self.add_source_code_line('# {}. polyline path'.format(count))
                self.add_source_code_line('e.path.add_polyline_path([')
                self.add_source_code_lines(fmt_list(path.vertices, indent=8))
                self.add_source_code_line('    ],')
                self.add_source_code_line(arg.format('is_closed', str(path.is_closed)))
                self.add_source_code_line(arg.format('flags', str(path.path_type_flags)))
                self.add_source_code_line(')')
            else:  # EdgePath
                self.add_source_code_line('# {}. edge path: associative hatch not supported'.format(count))
                self.add_source_code_line('ep = e.path.add_edge_path(flags={})'.format(path.path_type_flags))
                for edge in path.edges:
                    if edge.EDGE_TYPE == 'LineEdge':
                        self.add_source_code_line('ep.add_line({}, {})'.format(str(edge.start[:2]), str(edge.end[:2])))
                    elif edge.EDGE_TYPE == 'ArcEdge':
                        self.add_source_code_line('ep.add_arc(')
                        self.add_source_code_line(arg.format('center', str(edge.center[:2])))
                        self.add_source_code_line(arg.format('radius', edge.radius))
                        self.add_source_code_line(arg.format('start_angle', edge.start_angle))
                        self.add_source_code_line(arg.format('end_angle', edge.end_angle))
                        self.add_source_code_line(arg.format('is_counter_clockwise', edge.is_counter_clockwise))
                        self.add_source_code_line(')')
                    elif edge.EDGE_TYPE == 'EllipseEdge':
                        self.add_source_code_line('ep.add_ellipse(')
                        self.add_source_code_line(arg.format('center', str(edge.center[:2])))
                        self.add_source_code_line(arg.format('major_axis', str(edge.major_axis[:2])))
                        self.add_source_code_line(arg.format('ratio', edge.ratio))
                        self.add_source_code_line(arg.format('start_angle', edge.start_angle))
                        self.add_source_code_line(arg.format('end_angle', edge.end_angle))
                        self.add_source_code_line(arg.format('is_counter_clockwise', edge.is_counter_clockwise))
                        self.add_source_code_line(')')
                    elif edge.EDGE_TYPE == 'SplineEdge':
                        self.add_source_code_line('ep.add_spline(')
                        if edge.fit_points:
                            self.add_source_code_line(arg.format('fit_points', str([fp[:2] for fp in edge.fit_points])))
                        if edge.control_points:
                            self.add_source_code_line(
                                arg.format('control_points', str([cp[:2] for cp in edge.control_points])))
                        if edge.knot_values:
                            self.add_source_code_line(arg.format('knot_values', str(edge.knot_values)))
                        if edge.weights:
                            self.add_source_code_line(arg.format('weights', str(edge.weights)))
                        self.add_source_code_line(arg.format('degree', edge.degree))
                        self.add_source_code_line(arg.format('rational', edge.rational))
                        self.add_source_code_line(arg.format('periodic', edge.periodic))
                        self.add_source_code_line(')')
