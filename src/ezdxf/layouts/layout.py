# Created: 2019-02-18
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING, Iterable, Any, Union, List, Tuple, cast, Optional, Dict,
)
from ezdxf.math import Vec2
from ezdxf.entitydb import EntitySpace
from ezdxf.lldxf import const
from .base import BaseLayout

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        GeoData, SortEntsTable, Vertex, Viewport, Drawing, DXFLayout,
        DXFGraphic, BlockLayout,
    )


def get_block_entity_space(doc: 'Drawing',
                           block_record_handle: str) -> 'EntitySpace':
    block_record = doc.entitydb[block_record_handle]
    return block_record.entity_space


class Layout(BaseLayout):
    """
    Layout representation - base class for :class:`Modelspace` and
    :class:`Paperspace`

    Every layout consist of a LAYOUT entity in the OBJECTS section, an
    associated BLOCK in the BLOCKS section and a BLOCK_RECORD_TABLE entry.

    layout_key: handle of the BLOCK_RECORD, every layout entity has this
        handle as owner attribute (entity.dxf.owner)

    There are 3 different layout types:

        1. :class:`Modelspace`
        2. active :class:`Paperspace` layout
        3. inactive :class:`Paperspace` layout

    Internal Structure

    For every layout exist a :class:`BlockLayout` object in
    :class:`BlocksSection` and a :class:`Layout` object
    (as :class:`Modelspace` or :class:`Paperspace`) in :class:`Layouts`.

    The entity space of the :class:`BlockLayout` object and the entity space
    of the :class:`Layout` object are the same object.

    """
    # plot_layout_flags of LAYOUT entity
    PLOT_VIEWPORT_BORDERS = 1
    SHOW_PLOT_STYLES = 2
    PLOT_CENTERED = 4
    PLOT_HIDDEN = 8
    USE_STANDARD_SCALE = 16
    PLOT_PLOTSTYLES = 32
    SCALE_LINEWEIGHTS = 64
    PRINT_LINEWEIGHTS = 128
    DRAW_VIEWPORTS_FIRST = 512
    MODEL_TYPE = 1024
    UPDATE_PAPER = 2048
    ZOOM_TO_PAPER_ON_UPDATE = 4096
    INITIALIZING = 8192
    PREV_PLOT_INIT = 16384

    def __init__(self, layout: 'DXFLayout', doc: 'Drawing'):
        self.dxf_layout = layout
        block_record = doc.entitydb[layout.dxf.block_record_handle]
        # link maybe broken
        block_record.dxf.layout = layout.dxf.handle
        super().__init__(block_record)

    @classmethod
    def new(cls, name: str, block_name: str, doc: 'Drawing',
            dxfattribs: dict = None) -> 'Layout':
        """ Returns the required structures for a new layout:

            - a :class:`BlockLayout` with BLOCK_RECORD, BLOCK and ENDBLK entities
            - LAYOUT entity in the objects section

        Args:
            name: layout name as shown in tabs of CAD applications e.g. 'Layout2'
            block_name: layout block name e.g. '*Paper_Space2'
            doc: drawing document
            dxfattribs: additional DXF attributes for LAYOUT entity

        (internal API)

        """
        block_layout = doc.blocks.new(block_name)  # type: BlockLayout
        dxfattribs = dxfattribs or {}
        dxfattribs.update({
            'name': name,
            'block_record_handle': block_layout.block_record_handle
        })
        dxf_layout = doc.objects.new_entity('LAYOUT', dxfattribs=dxfattribs)
        return cls(dxf_layout, doc)

    @classmethod
    def load(cls, layout: 'DXFLayout', doc: 'Drawing'):
        """ Loading interface. (internal API) """
        layout = cls(layout, doc)
        layout._repair_owner_tags()
        return layout

    @property
    def name(self) -> str:
        """ Layout name as shown in tabs of :term:`CAD` applications. """
        return self.dxf_layout.dxf.name

    @property  # dynamic DXF attribute dispatching, e.g. DXFLayout.dxf.layout_flags
    def dxf(self) -> Any:
        """ Returns the DXF name space attribute of the associated
        :class:`~ezdxf.entities.DXFLayout` object.

        This enables direct access to the underlying LAYOUT entity,
        e.g. ``Layout.dxf.layout_flags``

        """
        return self.dxf_layout.dxf

    @property
    def block_record_name(self) -> str:
        """ Returns the name of the associated BLOCK_RECORD as string. """
        return self.block_record.dxf.name

    def _repair_owner_tags(self) -> None:
        """ Set `owner` and `paperspace` attributes of entities hosted by this
        layout to correct values.
        """
        layout_key = self.layout_key
        paperspace = 0 if self.is_modelspace else 1
        for entity in self:
            if entity.dxf.owner != layout_key:
                entity.dxf.owner = layout_key
            if entity.dxf.paperspace != paperspace:
                entity.dxf.paperspace = paperspace

    def __contains__(self, entity: Union['DXFGraphic', str]) -> bool:
        """ Returns ``True`` if `entity` is stored in this layout.

        Args:
             entity: :class:`DXFGraphic` object or handle as hex string

        """
        if isinstance(entity, str):  # entity is a handle string
            entity = self.entitydb[entity]
        return entity.dxf.owner == self.layout_key

    def destroy(self) -> None:
        """ Delete all entities and the layout itself from entity database and
        all linked structures.

        (internal API)
        """

        self.doc.objects.delete_entity(self.dxf_layout)
        # super() deletes block_record and associated entity space
        super().destroy()

    def get_sortents_table(self, create: bool = True) -> 'SortEntsTable':
        """ Get/Create the SORTENTSTABLE object associated to the layout.

        Args:
            create: new table if table do not exist and `create` is ``True``

        Raises:
            DXFValueError: if table not exist and `create` is ``False``

        (internal API)
        """
        xdict = self.get_extension_dict()
        try:
            sortents_table = xdict['ACAD_SORTENTS']
        except const.DXFKeyError:
            if create:
                sortents_table = self.doc.objects.new_entity(
                    'SORTENTSTABLE',
                    dxfattribs={
                        'owner': xdict.dxf.handle,
                        'block_record_handle': self.layout_key
                    },
                )
                xdict['ACAD_SORTENTS'] = sortents_table.dxf.handle
            else:
                raise const.DXFValueError(
                    'Extension dictionary entry ACAD_SORTENTS does not exist.')
        return sortents_table

    def set_redraw_order(self,
                         handles: Union[Dict, Iterable[Tuple[str, str]]]
                         ) -> None:
        """ If the header variable $SORTENTS `Regen` flag (bit-code value 16)
        is set, AutoCAD regenerates entities in ascending handles order.

        To change redraw order associate a different sort handle to entities,
        this redefines the order in which the entities are regenerated.
        `handles` can be a dict of entity_handle and sort_handle as (k, v)
        pairs, or an iterable of (entity_handle, sort_handle) tuples.

        The sort_handle doesn't have to be unique, some or all entities can
        share the same sort handle and a sort handle can be an existing handle.

        The "0" handle can be used, but this sort_handle will be drawn as
        latest (on top of all other entities) and not as first as expected.

        Args:
            handles: iterable or dict of handle associations; an iterable
                of 2-tuples (entity_handle, sort_handle) or a dict (k, v)
                association as (entity_handle, sort_handle)

        """
        sortents = self.get_sortents_table()
        if isinstance(handles, dict):
            handles = handles.items()
        sortents.set_handles(handles)

    def get_redraw_order(self) -> Iterable[Tuple[str, str]]:
        """ Returns iterable for all existing table entries as (entity_handle,
        sort_handle) pairs, see also :meth:`~Layout.set_redraw_order`.

        """
        empty = []
        if self.block_record.has_extension_dict:
            xdict = self.get_extension_dict()
        else:
            return empty

        try:
            sortents_table = xdict['ACAD_SORTENTS']
        except const.DXFKeyError:
            return empty
        return iter(sortents_table)

    def reset_extents(self, extmin=(+1e20, +1e20, +1e20),
                      extmax=(-1e20, -1e20, -1e20)) -> None:
        """ Reset `extents`_ to given values or the AutoCAD default values.

        "Drawing extents are the bounds of the area occupied by objects."
        (Quote Autodesk Knowledge Network)

        Args:
             extmin: minimum extents or (+1e20, +1e20, +1e20) as default value
             extmax: maximum extents or (-1e20, -1e20, -1e20) as default value

        """
        dxf = self.dxf_layout.dxf
        dxf.extmin = extmin
        dxf.extmax = extmax

    def reset_limits(self, limmin=None, limmax=None) -> None:
        """ Reset `limits`_ to given values or the AutoCAD default values.

        "Sets an invisible rectangular boundary in the drawing area that can
        limit the grid display and limit clicking or entering point locations."
        (Quote Autodesk Knowledge Network)

        The :class:`Paperspace` class has an additional method
        :meth:`~Paperspace.reset_paper_limits` to deduce the default limits from
        the paper size settings.

        Args:
             extmin: minimum extents or (0, 0) as default
             extmax: maximum extents or (paper width, paper height) as default value

        """
        dxf = self.dxf_layout.dxf
        if limmin is None:
            limmin = (0, 0)
        if limmax is None:
            limmax = (dxf.paper_width, dxf.paper_height)

        dxf.limmin = limmin
        dxf.limmax = limmax

    def set_plot_type(self, value: int = 5) -> None:
        """
        === ============================================================
        0   last screen display
        1   drawing extents
        2   drawing limits
        3   view specific (defined by :attr:`Layout.dxf.plot_view_name`)
        4   window specific (defined by :meth:`Layout.set_plot_window_limits`)
        5   layout information (default)
        === ============================================================

        Args:
            value:  plot type

        Raises:
            DXFValueError: for `value` out of range

        """
        if 0 <= int(value) <= 5:
            self.dxf.plot_type = value
        else:
            raise const.DXFValueError('Plot type value out of range (0-5).')

    def set_plot_style(self, name: str = 'ezdxf.ctb',
                       show: bool = False) -> None:
        """ Set plot style file of type `.ctb`.

        Args:
            name: plot style filename
            show: show plot style effect in preview? (AutoCAD specific attribute)

        """
        self.dxf_layout.dxf.current_style_sheet = name
        self.use_plot_styles(True)
        self.show_plot_styles(show)

    def set_plot_window(self,
                        lower_left: Tuple[float, float] = (0, 0),
                        upper_right: Tuple[float, float] = (0, 0)) -> None:
        """ Set plot window size in (scaled) paper space units.

        Args:
            lower_left: lower left corner as 2D point
            upper_right: upper right corner as 2D point

        """
        x1, y1 = lower_left
        x2, y2 = upper_right
        dxf = self.dxf_layout.dxf
        dxf.plot_window_x1 = x1
        dxf.plot_window_y1 = y1
        dxf.plot_window_x2 = x2
        dxf.plot_window_y2 = y2
        self.set_plot_type(4)

    # plot layout flags setter
    def plot_viewport_borders(self, state: bool = True) -> None:
        self.set_plot_flags(self.PLOT_VIEWPORT_BORDERS, state)

    def show_plot_styles(self, state: bool = True) -> None:
        self.set_plot_flags(self.SHOW_PLOT_STYLES, state)

    def plot_centered(self, state: bool = True) -> None:
        self.set_plot_flags(self.PLOT_CENTERED, state)

    def plot_hidden(self, state: bool = True) -> None:
        self.set_plot_flags(self.PLOT_HIDDEN, state)

    def use_standard_scale(self, state: bool = True) -> None:
        self.set_plot_flags(self.USE_STANDARD_SCALE, state)

    def use_plot_styles(self, state: bool = True) -> None:
        self.set_plot_flags(self.PLOT_PLOTSTYLES, state)

    def scale_lineweights(self, state: bool = True) -> None:
        self.set_plot_flags(self.SCALE_LINEWEIGHTS, state)

    def print_lineweights(self, state: bool = True) -> None:
        self.set_plot_flags(self.PRINT_LINEWEIGHTS, state)

    def draw_viewports_first(self, state: bool = True) -> None:
        self.set_plot_flags(self.PRINT_LINEWEIGHTS, state)

    def model_type(self, state: bool = True) -> None:
        self.set_plot_flags(self.MODEL_TYPE, state)

    def update_paper(self, state: bool = True) -> None:
        self.set_plot_flags(self.UPDATE_PAPER, state)

    def zoom_to_paper_on_update(self, state: bool = True) -> None:
        self.set_plot_flags(self.ZOOM_TO_PAPER_ON_UPDATE, state)

    def plot_flags_initializing(self, state: bool = True) -> None:
        self.set_plot_flags(self.INITIALIZING, state)

    def prev_plot_init(self, state: bool = True) -> None:
        self.set_plot_flags(self.PREV_PLOT_INIT, state)

    def set_plot_flags(self, flag, state: bool = True) -> None:
        self.dxf_layout.set_flag_state(flag, state=state,
                                       name='plot_layout_flags')


class Modelspace(Layout):
    """ :class:`Modelspace` - not deletable, all entities of this layout are
    stored in the ENTITIES section of the DXF file, the associated
    "*Model_Space" block is empty, block name is fixed as "*Model_Space",
    the name is fixed as ""Model".

    """

    @property
    def name(self) -> str:
        """ Name of modelspace is fixed as "Model". """
        return 'Model'

    def new_geodata(self, dxfattribs: dict = None) -> 'GeoData':
        """ Creates a new :class:`GeoData` entity and replaces existing ones.
        The GEODATA entity resides in the OBJECTS section and not in the
        modelspace, it is linked to the modelspace by an
        :class:`~ezdxf.entities.ExtensionDict` located in BLOCK_RECORD of the
        modelspace.

        The GEODATA entity requires DXF R2010. The DXF reference does not
        document if other layouts than the modelspace supports geo referencing,
        so I assume getting/setting geo data may only make sense for the
        modelspace.

        Args:
            dxfattribs: DXF attributes for :class:`~ezdxf.entities.GeoData` entity

        """
        if self.doc.dxfversion < const.DXF2010:
            raise const.DXFValueError(
                'GEODATA entity requires DXF R2010 or later.')

        if dxfattribs is None:
            dxfattribs = {}
        xdict = self.get_extension_dict()
        geodata = self.doc.objects.add_geodata(
            owner=xdict.dictionary.dxf.handle,
            dxfattribs=dxfattribs,
        )
        xdict['ACAD_GEOGRAPHICDATA'] = geodata
        return geodata

    def get_geodata(self) -> Optional['GeoData']:
        """ Returns the :class:`~ezdxf.entities.GeoData` entity associated to
        the modelspace or ``None``.
        """
        try:
            xdict = self.block_record.get_extension_dict()
        except AttributeError:
            return None
        try:
            return xdict['ACAD_GEOGRAPHICDATA']
        except const.DXFKeyError:
            return None


class Paperspace(Layout):
    """ There are two kind of paperspace layouts:

    1. Active Layout - all entities of this layout are stored in the ENTITIES
       section, the associated "*Paper_Space" block is empty, block name
       "*Paper_Space" is mandatory and also marks the active layout, the layout
       name can be an arbitrary string.

    2. Inactive Layout - all entities of this layouts are stored in the
       associated BLOCK called "*Paper_SpaceN", where "N" is an arbitrary
       number, I don't know if the block name schema "*Paper_SpaceN" is
       mandatory, the layout name can be an arbitrary string.

    There is no different handling for active layouts and inactive layouts in
    `ezdxf`, this differentiation is just for AutoCAD important and it is not
    documented in the DXF reference.

    """

    def rename(self, name: str) -> None:
        """ Rename layout to `name`, changes the name displayed in tabs by
        CAD applications, not the internal BLOCK name. (internal API)

        Use method :meth:`~ezdxf.layouts.Layouts.rename` of the
        :meth:`~ezdxf.layouts.Layouts` class to rename paper space
        layouts.

        """
        self.dxf_layout.dxf.name = name

    def viewports(self) -> List['Viewport']:
        """ Get all VIEWPORT entities defined in this paperspace layout.
        Returns a list of :class:`~ezdxf.entities.Viewport` objects, sorted by
        id, the first entity is always the main viewport with an id of 1.

        """
        vports = [entity for entity in self if entity.dxftype() == 'VIEWPORT']
        vports.sort(key=lambda e: e.dxf.id)
        return vports

    def main_viewport(self) -> Optional['Viewport']:
        """ Returns the main viewport of this paper space layout, or ``None``
        if no main viewport exist.

        """
        viewports = self.viewports()
        if len(viewports):
            return viewports[0]
        else:
            return None

    def renumber_viewports(self) -> None:
        """ Reassign viewport ids. (internal API) """
        for num, viewport in enumerate(self.viewports(), start=1):
            viewport.dxf.id = num

    def add_viewport(self, center: 'Vertex',
                     size: Tuple[float, float],
                     view_center_point: 'Vertex',
                     view_height: float,
                     dxfattribs: dict = None) -> 'Viewport':
        """ Add a new :class:`~ezdxf.entities.Viewport` entity. """
        dxfattribs = dxfattribs or {}
        width, height = size
        attribs = {
            'center': center,
            'width': width,
            'height': height,
            'status': 1,  # by default highest priority (stack order)
            'layer': 'VIEWPORTS',
            # use separated layer to turn off for plotting
            'view_center_point': view_center_point,
            'view_height': view_height,
        }
        attribs.update(dxfattribs)
        viewport = cast('Viewport', self.new_entity('VIEWPORT', attribs))
        viewport.dxf.id = viewport.get_next_viewport_id()
        return viewport

    def reset_viewports(self) -> None:
        """ Delete all existing viewports, and create a new main viewport. """
        # remove existing viewports
        for viewport in self.viewports():
            self.delete_entity(viewport)
        self.add_new_main_viewport()

    def reset_main_viewport(self, center: 'Vertex' = None,
                            size: 'Vertex' = None) -> 'Viewport':
        """ Reset the main viewport of this paper space layout to the given
        values, or reset them to the default values, deduced from the paper
        settings. Creates a new main viewport if none exist.

        Ezdxf does not create a main viewport by default, because CAD
        applications don't require one.

        Args:
            center: center of the viewport in paper space units
            size: viewport size as (width, height) tuple in paper space units

        """
        viewports = self.viewports()
        if len(viewports) == 0 or viewports[0].dxf.id != 1:
            viewport = self.add_new_main_viewport()
        else:
            viewport = viewports[0]
        default_center, default_size = self.default_viewport_config()
        if center is None:
            center = default_center
        if size is None:
            size = default_size

        viewport.dxf.center = center
        width, height = size
        viewport.dxf.width = width
        viewport.dxf.height = height
        return viewport

    def default_viewport_config(self) -> Tuple[Tuple[float, float],
                                               Tuple[float, float]]:
        dxf = self.dxf_layout.dxf
        if dxf.plot_paper_units == 0:  # inches
            unit_factor = 25.4
        else:  # mm
            unit_factor = 1.0

        # all paper parameters in mm!
        # all viewport parameters in paper space units inch/mm + scale factor!
        scale_factor = dxf.scale_denominator / dxf.scale_numerator

        def paper_units(value):
            return value / unit_factor * scale_factor

        paper_width = paper_units(dxf.paper_width)
        paper_height = paper_units(dxf.paper_height)
        # plot origin offset
        x_offset = paper_units(dxf.plot_origin_x_offset)
        y_offset = paper_units(dxf.plot_origin_y_offset)

        # printing area
        printable_width = paper_width - paper_units(
            dxf.left_margin) - paper_units(dxf.right_margin)
        printable_height = paper_height - paper_units(
            dxf.bottom_margin) - paper_units(dxf.top_margin)

        # AutoCAD viewport (window) size
        vp_width = paper_width * 1.1
        vp_height = paper_height * 1.1

        # center of printing area
        center = (
            printable_width / 2 - x_offset, printable_height / 2 - y_offset)
        return center, (vp_width, vp_height)

    def add_new_main_viewport(self) -> 'Viewport':
        """ Add a new main viewport. """
        center, size = self.default_viewport_config()
        vp_height = size[1]
        # create 'main' viewport
        main_viewport = self.add_viewport(
            center=center,  # no influence to 'main' viewport?
            size=size,  # I don't get it, just use paper size!
            view_center_point=center,  # same as center
            view_height=vp_height,  # view height in paper space units
        )
        main_viewport.dxf.id = 1  # set as main viewport
        main_viewport.dxf.flags = 557088  # AutoCAD default value
        self.dxf_layout.dxf.viewport_handle = main_viewport.dxf.handle
        return main_viewport

    def page_setup(self, size: Tuple[float, float] = (297, 210),
                   margins: Tuple[float, float, float, float] = (
                           10, 15, 10, 15),
                   units: str = 'mm',
                   offset: Tuple[float, float] = (0, 0),
                   rotation: int = 0,
                   scale: int = 16,
                   name: str = 'ezdxf',
                   device: str = 'DWG to PDF.pc3') -> None:
        """ Setup plot settings and paper size and reset viewports.
        All parameters in given `units` (mm or inch).

        Reset paper limits, extents and viewports.

        Args:
            size: paper size as (width, height) tuple
            margins: (top, right, bottom, left) hint: clockwise
            units: "mm" or "inch"
            offset: plot origin offset is 2D point
            rotation: see table Rotation
            scale: integer in range [0, 32] defines a standard scale type or
                as tuple(numerator, denominator) e.g. (1, 50) for scale 1:50
            name: paper name prefix "{name}_({width}_x_{height}_{unit})"
            device: device .pc3 configuration file or system printer name

        === ============
        int Rotation
        === ============
        0   no rotation
        1   90 degrees counter-clockwise
        2   upside-down
        3   90 degrees clockwise
        === ============

        """
        if int(rotation) not in (0, 1, 2, 3):
            raise const.DXFValueError("valid rotation values: 0-3")

        if isinstance(scale, tuple):
            standard_scale = 16
        elif isinstance(scale, int):
            standard_scale = scale
            scale = const.STD_SCALES.get(standard_scale, (1, 1))
        else:
            raise const.DXFTypeError(
                "Scale has to be an int or a tuple(numerator, denominator)")
        if scale[0] == 0:
            raise const.DXFValueError("Scale numerator can't be 0.")
        if scale[1] == 0:
            raise const.DXFValueError("Scale denominator can't be 0.")

        self.use_standard_scale(False)  # works best, don't know why
        paper_width, paper_height = size
        margin_top, margin_right, margin_bottom, margin_left = margins
        units = units.lower()
        if units.startswith('inch'):
            units = 'Inches'
            plot_paper_units = 0
            unit_factor = 25.4  # inch to mm
        elif units == 'mm':
            units = 'MM'
            plot_paper_units = 1
            unit_factor = 1.0
        else:
            raise const.DXFValueError('Supported units: "mm" and "inch"')

        # Setup PLOTSETTINGS
        # all paper sizes in mm
        dxf = self.dxf_layout.dxf
        dxf.page_setup_name = ''
        dxf.plot_configuration_file = device
        dxf.paper_size = f'{name}_({paper_width:.2f}_x_{paper_height:.2f}_{units})'
        dxf.left_margin = margin_left * unit_factor
        dxf.bottom_margin = margin_bottom * unit_factor
        dxf.right_margin = margin_right * unit_factor
        dxf.top_margin = margin_top * unit_factor
        dxf.paper_width = paper_width * unit_factor
        dxf.paper_height = paper_height * unit_factor
        dxf.scale_numerator = scale[0]
        dxf.scale_denominator = scale[1]
        dxf.plot_paper_units = plot_paper_units
        dxf.plot_rotation = rotation

        x_offset, y_offset = offset
        dxf.plot_origin_x_offset = x_offset * unit_factor  # conversion to mm
        dxf.plot_origin_y_offset = y_offset * unit_factor  # conversion to mm
        dxf.standard_scale_type = standard_scale
        dxf.unit_factor = 1. / unit_factor  # 1/1 for mm; 1/25.4 ... for inch

        # Setup Layout
        self.reset_paper_limits()
        self.reset_extents()
        self.reset_viewports()

    def reset_paper_limits(self) -> None:
        """ Set paper limits to default values, all values in paperspace units
        but without plot scale (?).

        """
        dxf = self.dxf_layout.dxf
        if dxf.plot_paper_units == 0:  # inch
            unit_factor = 25.4
        else:  # mm
            unit_factor = 1.0

        # all paper sizes are stored in mm
        paper_width = dxf.paper_width / unit_factor  # in plot paper units
        paper_height = dxf.paper_height / unit_factor  # in plot paper units
        left_margin = dxf.left_margin / unit_factor
        bottom_margin = dxf.bottom_margin / unit_factor
        x_offset = dxf.plot_origin_x_offset / unit_factor
        y_offset = dxf.plot_origin_y_offset / unit_factor
        # plot origin is the lower left corner of the printable paper area
        # limits are the paper borders relative to the plot origin
        shift_x = left_margin + x_offset
        shift_y = bottom_margin + y_offset
        dxf.limmin = (-shift_x, -shift_y)  # paper space units
        dxf.limmax = (paper_width - shift_x, paper_height - shift_y)

    def get_paper_limits(self) -> Tuple[Vec2, Vec2]:
        """  Returns paper limits in plot paper units, relative to the plot origin.

        plot origin = lower left corner of printable area + plot origin offset

        Returns:
            tuple (Vec2(x1, y1), Vec2(x2, y2)), lower left corner is (x1, y1),
            upper right corner is (x2, y2).

        """
        return Vec2(self.dxf.limmin), Vec2(self.dxf.limmax)

    def page_setup_r12(self, size: Tuple[int, int] = (297, 210),
                       margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
                       units: str = 'mm',
                       offset: Tuple[int, int] = (0, 0),
                       rotation: float = 0,
                       scale: int = 16) -> None:

        # remove existing viewports
        for viewport in self.viewports():
            self.delete_entity(viewport)

        if int(rotation) not in (0, 1, 2, 3):
            raise const.DXFValueError("Valid rotation values: 0-3")

        if isinstance(scale, int):
            scale = const.STD_SCALES.get(scale, (1, 1))

        if scale[0] == 0:
            raise const.DXFValueError("Scale numerator can't be 0.")
        if scale[1] == 0:
            raise const.DXFValueError("Scale denominator can't be 0.")

        scale_factor = scale[1] / scale[0]

        # TODO: don't know how to set inch or mm mode in R12
        units = units.lower()
        if units.startswith('inch'):
            units = 'Inches'
            plot_paper_units = 0
            unit_factor = 25.4  # inch to mm
        elif units == 'mm':
            units = 'MM'
            plot_paper_units = 1
            unit_factor = 1.0
        else:
            raise const.DXFValueError('Supported units: "mm" and "inch"')

        # all viewport parameters are scaled paper space units
        def paper_units(value):
            return value * scale_factor

        # TODO: don't know how paper setup in DXF R12 works
        paper_width, paper_height = size

        # TODO: don't know how margins setup in DXF R12 works
        margin_top, margin_right, margin_bottom, margin_left = margins

        paper_width = paper_units(size[0])
        paper_height = paper_units(size[1])

        plimmin = self.doc.header['$PLIMMIN'] = (0, 0)
        plimmax = self.doc.header['$PLIMMAX'] = (paper_width, paper_height)

        # TODO: don't know how paper setup in DXF R12 works

        pextmin = self.doc.header['$PEXTMIN'] = (0, 0, 0)
        pextmax = self.doc.header['$PEXTMAX'] = (paper_width, paper_height, 0)

        # printing area
        printable_width = paper_width - paper_units(margin_left) - paper_units(
            margin_right)
        printable_height = paper_height - paper_units(
            margin_bottom) - paper_units(margin_top)

        # AutoCAD viewport (window) size
        vp_width = paper_width * 1.1
        vp_height = paper_height * 1.1

        # center of printing area
        center = (printable_width / 2, printable_height / 2)

        # create 'main' viewport
        main_viewport = self.add_viewport(
            center=center,  # no influence to 'main' viewport?
            size=(vp_width, vp_height),  # I don't get it, just use paper size!
            view_center_point=center,  # same as center
            view_height=vp_height,  # view height in paper space units
        )
        main_viewport.dxf.id = 1  # set as main viewport
        main_viewport.dxf.status = 2  # AutoCAD default value
        with main_viewport.edit_data() as vpdata:
            vpdata.view_mode = 1000  # AutoDesk default

    def get_paper_limits_r12(self) -> Tuple[Vec2, Vec2]:
        """  Returns paper limits in plot paper units. """
        limmin = self.doc.header.get('$PLIMMIN', (0, 0))
        limmax = self.doc.header.get('$PLIMMAX', (0, 0))
        return Vec2(limmin), Vec2(limmax)
