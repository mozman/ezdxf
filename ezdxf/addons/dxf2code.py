# Created: 17.05.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
"""
Translate DXF entities and structures into Python source code.

"""
from typing import TYPE_CHECKING, Iterable, List, TextIO, Mapping, Set
import json

from ezdxf.sections.tables import TABLENAMES
from ezdxf.lldxf.tags import Tags

if TYPE_CHECKING:
    from ezdxf.eztypes import Insert, MText, LWPolyline, Polyline, Spline, Leader, Dimension, Image, Mesh, Hatch
    from ezdxf.eztypes import DXFEntity, Linetype, DXFTag, BlockLayout

__all__ = ['entities_to_code', 'block_to_code', 'table_entries_to_code']


def entities_to_code(entities: Iterable['DXFEntity'], layout: str = 'layout',
                     ignore: Iterable[str] = None) -> 'SourceCodeGenerator':
    """
    Translates DXF entities into Python source code to recreate this entities by ezdxf.

    Args:
        entities: iterable of DXFEntity
        layout: variable name of the layout (model space or block)
        ignore: iterable of entities types to ignore as strings like ['IMAGE', 'DIMENSION']

    Returns: :class:`SourceCodeGenerator`

    """
    code_generator = SourceCodeGenerator(layout=layout)
    code_generator.translate_entities(entities, ignore=ignore)
    return code_generator


def block_to_code(block: 'BlockLayout', drawing: str = 'doc', ignore: Iterable[str] = None) -> 'SourceCodeGenerator':
    """
    Translates a BLOCK into Python source code to recreate the BLOCK by ezdxf.

    Args:
        block: block definition layout
        drawing: variable name of the drawing
        ignore: iterable of entities types to ignore as strings like ['IMAGE', 'DIMENSION']

    Returns: :class:`SourceCodeGenerator`

    """
    dxfattribs = purge_handles(block.block.dxfattribs())
    block_name = dxfattribs.pop('name')
    base_point = dxfattribs.pop('base_point')
    code = SourceCodeGenerator(layout='block')
    prolog = 'block = {}.blocks.new("{}", base_point={}, dxfattribs={{'.format(drawing, block_name, str(base_point))
    code.add_source_code_line(prolog)
    code.add_source_code_lines(fmt_mapping(dxfattribs, indent=4))
    code.add_source_code_line('    }')
    code.add_source_code_line(')')
    code.translate_entities(block, ignore=ignore)
    return code


def table_entries_to_code(entities: Iterable['DXFEntity'], drawing='doc') -> 'SourceCodeGenerator':
    code = SourceCodeGenerator(doc=drawing)
    code.translate_entities(entities)
    return code


PURGE_DXF_ATTRIBUTES = {'handle', 'owner', 'paperspace', 'material_handle', 'visualstyle_handle', 'plotstyle_handle'}


def purge_handles(attribs: dict) -> dict:
    """
    Purge handles from DXF attributes which will be invalid in a new document, or which will be set automatically by
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
        yield fmt.format(str(v))


def fmt_api_call(func_call: str, args: Iterable[str], dxfattribs: dict) -> List[str]:
    attributes = dict(dxfattribs)
    args = list(args) if args else []

    def fmt_keywords() -> Iterable[str]:
        for arg in args:
            if arg not in attributes:
                continue
            value = attributes.pop(arg)
            if isinstance(value, str):
                valuestr = json.dumps(value)  # quoted string!
            else:
                valuestr = str(value)
            yield "    {}={},".format(arg, valuestr)

    s = [func_call]
    s.extend(fmt_keywords())
    s.append('    dxfattribs={')
    s.extend(fmt_mapping(attributes, indent=8))
    s.extend([
        "    },",
        ")",
    ])
    return s


def fmt_dxf_tags(tags: Iterable['DXFTag'], indent: int = 0):
    fmt = ' ' * indent + 'dxftag({}, {}),'
    for code, value in tags:
        assert isinstance(code, int)
        if isinstance(value, str):
            value = json.dumps(value)  # for correct escaping of quotes
        else:
            value = str(value)  # format uses repr() for Vectors
        yield fmt.format(code, value)


class SourceCodeGenerator:
    """
    The SourceCodeGenerator translates DXF entities into Python source code for creating the same DXF entity in another
    model space or block definition.

    Args:
        layout: variable name of the layout (model space or block), required for graphical entities
        doc: variable name of the document, required for table entries

    """

    def __init__(self, layout: str = 'layout', doc: str = 'doc'):
        self.doc = doc
        self.layout = layout
        self.source_code = []  # type: List[str]
        self.used_layers = set()  # type: Set[str]  # layer names as string
        self.used_styles = set()  # type: Set[str]  # text style name as string, requires a TABLE entry
        self.used_linetypes = set()  # type: Set[str]  # line type names as string, requires a TABLE entry
        self.used_dimstyles = set()  # type: Set[str]  # dimension style names as string, requires a TABLE entry
        self.used_blocks = set()  # type: Set[str]  # block names as string, requires a BLOCK definition
        self.required_imports = set()  # type: Set[str]

    def translate_entity(self, entity: 'DXFEntity') -> None:
        """
        Translates one DXF entity into Python source code. The generated source code is appended to the
        attribute `source_code`.

        Args:
            entity: DXFEntity object

        """
        dxftype = entity.dxftype()
        try:
            entity_translator = getattr(self, '_' + dxftype.lower())
        except AttributeError:
            self.add_source_code_line('# unsupported DXF entity "{}"'.format(dxftype))
        else:
            entity_translator(entity)

    def translate_entities(self, entities: Iterable['DXFEntity'], ignore: Iterable[str] = None) -> None:
        """
        Translates multiple DXF entities into Python source code. The generated source code is appended to the
        attribute `source_code`.

        Args:
            entities: iterable of DXFEntity
            ignore: iterable of entities types to ignore as strings like ['IMAGE', 'DIMENSION']

        """
        ignore = set(ignore) if ignore else set()

        for entity in entities:
            if entity.dxftype() not in ignore:
                self.translate_entity(entity)

    def add_used_resources(self, dxfattribs: Mapping) -> None:
        """
        Register used resources like layers, line types, text styles and dimension styles.

        Args:
            dxfattribs: DXF attributes dictionary

        """
        if 'layer' in dxfattribs:
            self.used_layers.add(dxfattribs['layer'])
        if 'linetype' in dxfattribs:
            self.used_linetypes.add(dxfattribs['linetype'])
        if 'style' in dxfattribs:
            self.used_styles.add(dxfattribs['style'])
        if 'dimstyle' in dxfattribs:
            self.used_dimstyles.add(dxfattribs['dimstyle'])

    def add_import_statement(self, statement: str) -> None:
        self.required_imports.add(statement)

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

    def add_tags_source_code(self, tags: Tags, prolog='tags = Tags(', epilog=')', indent=4):
        fmt_str = ' ' * indent + '{}'
        self.add_source_code_line(fmt_str.format(prolog))
        self.add_source_code_lines(fmt_dxf_tags(tags, indent=4 + indent))
        self.add_source_code_line(fmt_str.format(epilog))

    def generic_api_call(self, dxftype: str, dxfattribs: dict, prefix: str = 'e = ') -> Iterable[str]:
        """
        Returns the source code strings to create a DXF entity by a generic `new_entity()` call.

        Args:
            dxftype: DXF entity type as string, like 'LINE'
            dxfattribs: DXF attributes dictionary
            prefix: prefix string like variable assignment 'e = '

        """
        dxfattribs = purge_handles(dxfattribs)
        self.add_used_resources(dxfattribs)
        s = [
            "{}{}.new_entity(".format(prefix, self.layout),
            "    '{}',".format(dxftype),
            "    dxfattribs={",
        ]
        s.extend(fmt_mapping(dxfattribs, indent=8))
        s.extend([
            "    },",
            ")",
        ])
        return s

    def api_call(self, api_call: str, args: Iterable[str], dxfattribs: dict, prefix: str = 'e = ') -> Iterable[str]:
        """
        Returns the source code strings to create a DXF entity by the specialised API call.

        Args:
            api_call: API function call like 'add_line('
            args: DXF attributes to pass as arguments
            dxfattribs: DXF attributes dictionary
            prefix: prefix string like variable assignment 'e = '
        """
        dxfattribs = purge_handles(dxfattribs)
        func_call = '{}{}.{}'.format(prefix, self.layout, api_call)
        return fmt_api_call(func_call, args, dxfattribs)

    def new_table_entry(self, dxftype: str, dxfattribs: dict) -> Iterable[str]:
        """
        Returns the source code strings to create a new table entity by ezdxf.

        Args:
            dxftype: table entry type as string, like 'LAYER'
            dxfattribs: DXF attributes dictionary

        """
        table = '{}.{}'.format(self.doc, TABLENAMES[dxftype])
        dxfattribs = purge_handles(dxfattribs)
        name = dxfattribs.pop('name')
        s = [
            "if '{}' not in {}:".format(name, table),
            "    t = {}.new(".format(table),
            "        '{}',".format(name),
            "        dxfattribs={",
        ]
        s.extend(fmt_mapping(dxfattribs, indent=12))
        s.extend([
            "        },",
            "    )",
        ])
        return s

    def imports(self, indent: int = 0) -> str:
        lead_str = ' ' * indent
        return '\n'.join(lead_str + line for line in self.required_imports)

    def tostring(self, indent: int = 0) -> str:
        lead_str = ' ' * indent
        return '\n'.join(lead_str + line for line in self.source_code)

    def __str__(self) -> str:
        return self.tostring()

    def writelines(self, stream: TextIO, indent: int = 0):
        fmt = ' ' * indent + '{}\n'
        for line in self.source_code:
            stream.write(fmt.format(line))

    # simple graphical types

    def _line(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_line(', ['start', 'end'], entity.dxfattribs()))

    def _point(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_point(', ['location'], entity.dxfattribs()))

    def _circle(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_circle(', ['center', 'radius'], entity.dxfattribs()))

    def _arc(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(
            self.api_call('add_arc(', ['center', 'radius', 'start_angle', 'end_angle'], entity.dxfattribs()))

    def _text(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_text(', ['text'], entity.dxfattribs()))

    def _solid(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.generic_api_call('SOLID', entity.dxfattribs()))

    def _trace(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.generic_api_call('TRACE', entity.dxfattribs()))

    def _3dface(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.generic_api_call('3DFACE', entity.dxfattribs()))

    def _shape(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_shape(', ['name', 'insert', 'size'], entity.dxfattribs()))

    def _attrib(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.api_call('add_attrib(', ['tag', 'text', 'insert'], entity.dxfattribs()))

    def _attdef(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.generic_api_call('ATTDEF', entity.dxfattribs()))

    def _ellipse(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(
            self.api_call('add_ellipse(', ['center', 'major_axis', 'ratio', 'start_param', 'end_param'],
                          entity.dxfattribs()))

    def _viewport(self, entity: 'DXFEntity') -> None:
        self.add_source_code_lines(self.generic_api_call('VIEWPORT', entity.dxfattribs()))
        self.add_source_code_line('# Set valid handles or remove attributes ending with "_handle", otherwise the DXF '
                                  'file is invalid for AutoCAD')

    # complex graphical types

    def _insert(self, entity: 'Insert') -> None:
        self.used_blocks.add(entity.dxf.name)
        self.add_source_code_lines(self.api_call('add_blockref(', ['name', 'insert'], entity.dxfattribs()))
        if len(entity.attribs):
            for attrib in entity.attribs:
                dxfattribs = attrib.dxfattribs()
                dxfattribs['layer'] = entity.dxf.layer  # set ATTRIB layer to same as INSERT
                self.add_source_code_lines(self.generic_api_call('ATTRIB', attrib.dxfattribs(), prefix='a = '))
                self.add_source_code_lines('e.attribs.append(a)')

    def _mtext(self, entity: 'MText') -> None:
        self.add_source_code_lines(self.generic_api_call('MTEXT', entity.dxfattribs()))
        # mtext content 'text' is not a single DXF tag and therefore not a DXF attribute
        self.add_source_code_line('e.text = {}'.format(json.dumps(entity.text)))

    def _lwpolyline(self, entity: 'LWPolyline') -> None:
        self.add_source_code_lines(self.generic_api_call('LWPOLYLINE', entity.dxfattribs()))
        # lwpolyline points are not DXF attributes
        self.add_list_source_code(entity.get_points(), prolog='e.set_points([', epilog='])')

    def _spline(self, entity: 'Spline') -> None:
        self.add_source_code_lines(self.api_call('add_spline(', ['degree'], entity.dxfattribs()))
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
        self.add_source_code_lines(self.generic_api_call('POLYLINE', entity.dxfattribs()))
        # polyline vertices are separate DXF entities and therefore not DXF attributes
        for v in entity.vertices:
            attribs = purge_handles(v.dxfattribs())
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
        self.add_source_code_lines(self.generic_api_call('LEADER', entity.dxfattribs()))
        self.add_list_source_code(entity.vertices, prolog='e.set_vertices([', epilog='])')

    def _dimension(self, entity: 'Dimension'):
        self.add_import_statement('from ezdxf.dimstyleoverride import DimStyleOverride')
        self.add_source_code_line('# Dimension style attribute overriding is not supported!')
        self.add_source_code_lines(self.generic_api_call('DIMENSION', entity.dxfattribs()))
        self.add_source_code_lines([
            '# You have to create the required graphical representation for the DIMENSION entity as anonymous block, ',
            '# otherwise the DXF file is invalid for AutoCAD (but not for BricsCAD):',
            '# DimStyleOverride(e).render()',
            ''
        ])

    def _image(self, entity: 'Image'):
        self.add_source_code_line('# Image requires IMAGEDEF and IMAGEDEFREACTOR objects in the OBJECTS section!')
        self.add_source_code_lines(self.generic_api_call('IMAGE', entity.dxfattribs()))
        if len(entity.boundary_path):
            self.add_list_source_code(
                (v[:2] for v in entity.boundary_path),  # just x, y axis
                prolog='e.set_boundary_path([',
                epilog='])',
            )
        self.add_source_code_line('# Set valid image_def_handle and image_def_reactor_handle, otherwise the DXF file'
                                  ' is invalid for AutoCAD')

    def _mesh(self, entity: 'Mesh'):
        self.add_source_code_lines(self.api_call('add_mesh(', [], entity.dxfattribs()))
        if len(entity.vertices):
            self.add_list_source_code(entity.vertices, prolog='e.vertices = [', epilog=']')
        if len(entity.edges):
            # array.array -> tuple
            self.add_list_source_code((tuple(e) for e in entity.edges), prolog='e.edges = [', epilog=']')
        if len(entity.faces):
            # array.array -> tuple
            self.add_list_source_code((tuple(f) for f in entity.faces), prolog='e.faces = [', epilog=']')
        if len(entity.creases):
            self.add_list_source_code(entity.creases, prolog='e.creases = [', epilog=']')

    def _hatch(self, entity: 'Hatch'):
        add_line = self.add_source_code_line
        dxfattribs = entity.dxfattribs()
        dxfattribs['associative'] = 0  # associative hatch not supported
        self.add_source_code_lines(self.api_call('add_hatch(', ['color'], dxfattribs))
        if len(entity.seeds):
            add_line("e.set_seed_points({})".format(str(entity.seeds)))
        if entity.pattern:
            self.add_list_source_code(entity.pattern.lines, prolog='e.set_pattern_definition([', epilog='])')
        arg = "    '{}'={},"

        if entity.has_gradient_data:
            g = entity.gradient
            add_line('e.set_gradient(')
            add_line(arg.format('color1', str(g.color1)))
            add_line(arg.format('color2', str(g.color2)))
            add_line(arg.format('rotation', g.rotation))
            add_line(arg.format('centered', g.centered))
            add_line(arg.format('one_color', g.one_color))
            add_line(arg.format('name', json.dumps(g.name)))
            add_line(')')
        for count, path in enumerate(entity.paths, start=1):
            if path.PATH_TYPE == 'PolylinePath':
                add_line('# {}. polyline path'.format(count))
                self.add_list_source_code(path.vertices, prolog='e.path.add_polyline_path([', epilog='    ],')
                add_line(arg.format('is_closed', str(path.is_closed)))
                add_line(arg.format('flags', str(path.path_type_flags)))
                add_line(')')
            else:  # EdgePath
                add_line('# {}. edge path: associative hatch not supported'.format(count))
                add_line('ep = e.path.add_edge_path(flags={})'.format(path.path_type_flags))
                for edge in path.edges:
                    if edge.EDGE_TYPE == 'LineEdge':
                        add_line('ep.add_line({}, {})'.format(str(edge.start[:2]), str(edge.end[:2])))
                    elif edge.EDGE_TYPE == 'ArcEdge':
                        add_line('ep.add_arc(')
                        add_line(arg.format('center', str(edge.center[:2])))
                        add_line(arg.format('radius', edge.radius))
                        add_line(arg.format('start_angle', edge.start_angle))
                        add_line(arg.format('end_angle', edge.end_angle))
                        add_line(arg.format('is_counter_clockwise', edge.is_counter_clockwise))
                        add_line(')')
                    elif edge.EDGE_TYPE == 'EllipseEdge':
                        add_line('ep.add_ellipse(')
                        add_line(arg.format('center', str(edge.center[:2])))
                        add_line(arg.format('major_axis', str(edge.major_axis[:2])))
                        add_line(arg.format('ratio', edge.ratio))
                        add_line(arg.format('start_angle', edge.start_angle))
                        add_line(arg.format('end_angle', edge.end_angle))
                        add_line(arg.format('is_counter_clockwise', edge.is_counter_clockwise))
                        add_line(')')
                    elif edge.EDGE_TYPE == 'SplineEdge':
                        add_line('ep.add_spline(')
                        if edge.fit_points:
                            add_line(arg.format('fit_points', str([fp[:2] for fp in edge.fit_points])))
                        if edge.control_points:
                            add_line(
                                arg.format('control_points', str([cp[:2] for cp in edge.control_points])))
                        if edge.knot_values:
                            add_line(arg.format('knot_values', str(edge.knot_values)))
                        if edge.weights:
                            add_line(arg.format('weights', str(edge.weights)))
                        add_line(arg.format('degree', edge.degree))
                        add_line(arg.format('rational', edge.rational))
                        add_line(arg.format('periodic', edge.periodic))
                        add_line(')')

    # simple table entries
    def _layer(self, layer: 'DXFEntity'):
        self.add_source_code_lines(self.new_table_entry('LAYER', layer.dxfattribs()))

    def _ltype(self, ltype: 'Linetype'):
        self.add_import_statement('from ezdxf.lldxf.tags import Tags')
        self.add_import_statement('from ezdxf.lldxf.types import dxftag')
        self.add_import_statement('from ezdxf.entities.ltype import LinetypePattern')
        self.add_source_code_lines(self.new_table_entry('LTYPE', ltype.dxfattribs()))
        self.add_tags_source_code(ltype.pattern_tags.tags, prolog='tags = Tags([', epilog='])', indent=4)
        self.add_source_code_line('    t.pattern_tags = LinetypePattern(tags)')

    def _style(self, style: 'DXFEntity'):
        self.add_source_code_lines(self.new_table_entry('STYLE', style.dxfattribs()))

    def _dimstyle(self, dimstyle: 'DXFEntity'):
        self.add_source_code_lines(self.new_table_entry('DIMSTYLE', dimstyle.dxfattribs()))

    def _appid(self, appid: 'DXFEntity'):
        self.add_source_code_lines(self.new_table_entry('APPID', appid.dxfattribs()))
