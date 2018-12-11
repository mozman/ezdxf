# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union, List, Iterable, Tuple, Dict, Hashable, Sequence, Optional
from ezdxf.graphicsfactory import GraphicsFactory
from ezdxf.entityspace import EntitySpace
from ezdxf.query import EntityQuery
from ezdxf.groupby import groupby
from ezdxf.lldxf.const import STD_SCALES, DXFValueError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, EntityDB, LayoutType, DXFEntity, TagWriter, DXFFactoryType, EntitySpace
    from ezdxf.eztypes import KeyFunc, GenericLayoutType


class DXF12Layouts:
    """
    The Layout container.

    """

    def __init__(self, drawing: 'Drawing'):
        entities = drawing.sections.entities
        model_space = entities.model_space_entities()
        self._modelspace = DXF12Layout(model_space, drawing.dxffactory, 0)
        paper_space = entities.active_layout_entities()
        self._paperspace = DXF12Layout(paper_space, drawing.dxffactory, 1)
        entities.clear()  # remove entities for entities section -> stored in layouts

    def __iter__(self) -> 'LayoutType':
        yield self._modelspace
        yield self._paperspace

    def __len__(self) -> int:
        return 2

    def modelspace(self) -> 'LayoutType':
        return self._modelspace

    def get(self, name: str = "") -> 'LayoutType':
        # AC1009 supports only one paperspace/layout
        return self._paperspace

    def names(self) -> List[str]:
        return []

    def get_layout_for_entity(self, entity: 'DXFEntity') -> 'LayoutType':
        # paperspace attribute defaults to 0 if not present
        if entity in self._modelspace:
            return self._modelspace
        elif entity in self._paperspace:
            return self._paperspace
        else:
            return None

    def active_layout(self) -> 'LayoutType':
        return self._paperspace

    def write_entities_section(self, tagwriter: 'TagWriter') -> None:
        self._modelspace.write(tagwriter)
        self._paperspace.write(tagwriter)


class BaseLayout(GraphicsFactory):
    """
    Base class for DXF12Layout() and DXF12BlockLayout()

    Entities are wrapped into class GraphicEntity() or inherited.

    """

    def __init__(self, dxffactory: 'DXFFactoryType', entity_space: 'EnitySpace'):
        super(BaseLayout, self).__init__(dxffactory)
        self._entity_space = entity_space

    def __len__(self) -> int:
        return len(self._entity_space)

    def __iter__(self) -> Iterable['DXFEntity']:
        """
        Iterate over all block entities, yielding class GraphicEntity() or inherited.

        """
        wrap = self._dxffactory.wrap_handle
        for handle in self._entity_space:
            yield wrap(handle)

    @property
    def entitydb(self) -> 'EnityDB':
        return self._dxffactory.entitydb

    @property
    def drawing(self) -> 'Drawing':
        return self._dxffactory.drawing

    def build_and_add_entity(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create entity in drawing database and add entity to the entity space.

        Args:
            type_ (str): DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
            dxfattribs (dict): DXF attributes for the new entity

        """
        entity = self.build_entity(type_, dxfattribs)
        self.add_entity(entity)
        return entity

    def build_entity(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create entity in drawing database, returns a wrapper class inherited from GraphicEntity().

        Adds entity to the drawing database.

        Args:
            type_ (str): DXF type string, like 'LINE', 'CIRCLE' or 'LWPOLYLINE'
            dxfattribs(dict): DXF attributes for the new entity

        """
        entity = self._dxffactory.create_db_entry(type_, dxfattribs)
        self._set_paperspace(entity)
        return entity

    def add_entity(self, entity: 'DXFEntity') -> None:
        """
        Add entity to entity space but not to the drawing database.

        """
        self._entity_space.append(entity.dxf.handle)
        self._set_paperspace(entity)
        for linked_entity in entity.linked_entities():
            self._set_paperspace(linked_entity)

    def unlink_entity(self, entity: 'DXFEntity') -> None:
        """
        Delete entity from entity space but not from the drawing database.

        """
        self._entity_space.delete_entity(entity)
        entity.dxf.paperspace = -1  # set invalid paper space
        if entity.supports_dxf_attrib('owner'):  # R2000
            entity.dxf.owner = '0'

    def delete_entity(self, entity: 'DXFEntity') -> None:
        """
        Delete entity from entity space and drawing database.

        """
        self.entitydb.delete_entity(entity)  # 1. delete from drawing database
        self.unlink_entity(entity)  # 2. unlink from entity space

    def delete_all_entities(self) -> None:
        """
        Delete all entities of this layout from entity space and from drawing database.

        Deletes only entities from this layout. Important because ALL layout entities are stored in just one entity
        space.

        """
        # noinspection PyTypeChecker
        for entity in list(self):  # temp list, because delete modifies the base data structure of the iterator
            self.delete_entity(entity)

    def _set_paperspace(self, entity: 'DXFEntity') -> None:
        pass  # only for DXF 2000 and later necessary

    def get_entity_by_handle(self, handle: str) -> 'DXFEntity':
        """
        Get entity by handle as GraphicEntity() or inherited.

        """
        return self._dxffactory.wrap_handle(handle)

    def query(self, query='*') -> EntityQuery:
        return EntityQuery(iter(self), query)

    def groupby(self, dxfattrib: str = "", key: 'KeyFunc' = None) -> Dict[Hashable, List['DXFEntity']]:
        return groupby(iter(self), dxfattrib, key)

    def move_to_layout(self, entity: 'DXFEntity', layout: 'GenericLayoutType') -> None:
        """
        Move entity from block layout to another layout.

        Args:
            entity: DXF entity to move
            layout: any layout (model space, paper space, block)

        """
        if entity.dxf.handle in self._entity_space:
            self.unlink_entity(entity)
            layout.add_entity(entity)
        else:
            raise DXFValueError('Layout does not contain entity.')


class DXF12Layout(BaseLayout):
    """
    Layout representation

    """

    def __init__(self, entityspace: 'EntitySpace', dxffactory: 'DXFFactoryType', paperspace: int = 0):
        super(DXF12Layout, self).__init__(dxffactory, entityspace)
        self._paperspace = paperspace

    # start of public interface

    def __contains__(self, entity: Union[str, 'DXFEntity']):
        """
        Returns True if layout contains entity else False. entity can be an entity handle as string or a wrapped
        dxf entity.

        """
        if not hasattr(entity, 'dxf'):  # entity is a handle and not a wrapper class
            entity = self.get_entity_by_handle(entity)
        return entity.dxf.paperspace == self._paperspace and entity.dxf.handle in self._entity_space

    # end of public interface

    def _set_paperspace(self, entity: 'DXFEntity'):
        entity.dxf.paperspace = self._paperspace

    def page_setup(self, size: Tuple[int, int] = (297, 210),
                   margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
                   units: str = 'mm',
                   offset: Tuple[int, int] = (0, 0),
                   rotation: float = 0,
                   scale: int = 16) -> None:
        if self._paperspace == 0:
            raise DXFTypeError("No paper setup for model space.")

        # remove existing viewports
        for viewport in self.viewports():
            self.delete_entity(viewport)

        if int(rotation) not in (0, 1, 2, 3):
            raise DXFValueError("valid rotation values: 0-3")

        if isinstance(scale, int):
            scale = STD_SCALES.get(scale, (1, 1))

        if scale[0] == 0:
            raise DXFValueError("scale numerator can't be 0.")
        if scale[1] == 0:
            raise DXFValueError("scale denominator can't be 0.")

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
            raise DXFValueError('Supported units: "mm" and "inch"')

        # all viewport parameters are scaled paper space units
        def paper_units(value):
            return value * scale_factor

        # TODO: don't know how paper setup in DXF R12 works
        paper_width, paper_height = size

        # TODO: don't know how margins setup in DXF R12 works
        margin_top, margin_right, margin_bottom, margin_left = margins

        paper_width = paper_units(size[0])
        paper_height = paper_units(size[1])

        plimmin = self.drawing.header['$PLIMMIN'] = (0, 0)
        plimmax = self.drawing.header['$PLIMMAX'] = (paper_width, paper_height)

        # TODO: don't know how paper setup in DXF R12 works

        pextmin = self.drawing.header['$PEXTMIN'] = (0, 0, 0)
        pextmax = self.drawing.header['$PEXTMAX'] = (paper_width, paper_height, 0)

        # printing area
        printable_width = paper_width - paper_units(margin_left) - paper_units(margin_right)
        printable_height = paper_height - paper_units(margin_bottom) - paper_units(margin_top)

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

    def get_paper_limits(self) -> Tuple[float, float]:
        """
        Returns paper limits in plot paper units

        """
        limmin = self.drawing.header.get('$PLIMMIN', (0, 0))
        limmax = self.drawing.header.get('$PLIMMAX', (0, 0))
        return limmin, limmax

    @property
    def layout_key(self) -> int:
        return self._paperspace

    def viewports(self) -> List['DXFEntity']:
        """
        Get all VIEWPORT entities defined in the layout. Returns a list of Viewport() objects, sorted by id, the first
        entity is always the paper space view with the id=1.

        """
        vports = [entity for entity in self if entity.dxftype() == 'VIEWPORT']
        vports.sort(key=lambda e: e.dxf.id)
        return vports

    def renumber_viewports(self) -> None:
        for num, viewport in enumerate(self.viewports(), start=1):
            viewport.dxf.id = num

    def write(self, tagwriter: 'TagWriter') -> None:
        self._entity_space.write(tagwriter)

    def add_viewport(self,
                     center: Tuple[float, float],
                     size: Tuple[float, float],
                     view_center_point: Tuple[float, float],
                     view_height: float,
                     dxfattribs: dict = None) -> 'DXFEntity':
        if dxfattribs is None:
            dxfattribs = {}
        else:
            dxfattribs = dict(dxfattribs)
        width, height = size
        attribs = {
            'center': center,
            'width': width,
            'height': height,
            'status': 1,  # by default highest priority (stack order)
            'layer': 'VIEWPORTS',  # use separated layer to turn off for plotting
        }
        attribs.update(dxfattribs)
        # DXF R12 (AC1009): view_center_point and view_height (as many other viewport attributes) are not usual
        # DXF attributes, they are stored as extended DXF tags.
        viewport = self.build_and_add_entity('VIEWPORT', attribs)
        viewport.dxf.id = viewport.get_next_viewport_id()
        with viewport.edit_data() as vp_data:
            vp_data.view_center_point = view_center_point
            vp_data.view_height = view_height
        return viewport


class DXF12BlockLayout(BaseLayout):
    """
    BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    Attributes:
        _block_handle: db handle to BLOCK entity
        _endblk_handle: db handle to ENDBLK entity
        _entityspace: is the block content

    """

    def __init__(self, entitydb: 'EntityDB', dxffactory: 'DXFFactoryType', block_handle: str, endblk_handle: str):
        super(DXF12BlockLayout, self).__init__(dxffactory, EntitySpace(entitydb))
        self._block_handle = block_handle
        self._endblk_handle = endblk_handle

    # start of public interface

    def __contains__(self, entity: 'DXFEntity') -> bool:
        """
        Returns True if block contains entity else False. *entity* can be a handle-string, Tags(),
        ExtendedTags() or a wrapped entity.

        """
        if hasattr(entity, 'get_handle'):
            handle = entity.get_handle()
        elif hasattr(entity, 'dxf'):  # it's a wrapped entity
            handle = entity.dxf.handle
        else:
            handle = entity
        return handle in self._entity_space

    @property
    def block(self) -> 'DXFEntity':
        """ Get associated BLOCK entity. """
        return self.get_entity_by_handle(self._block_handle)

    @property
    def endblk(self) -> 'DXFEntity':
        """ Get associated ENDBLK entity. """
        return self.get_entity_by_handle(self._endblk_handle)

    @property
    def name(self) -> str:
        """ Get block name """
        return self.block.dxf.name

    @name.setter
    def name(self, new_name) -> None:
        """ Set block name """
        block = self.block
        block.dxf.name = new_name
        block.dxf.name2 = new_name

    @property
    def is_layout_block(self) -> bool:
        """
        True if block is a model space or paper space block definition.

        """
        return self.block.is_layout_block

    def add_attdef(self, tag: str, insert: Sequence[float] = (0, 0), text: str = '',
                   dxfattribs: dict = None) -> 'DXFEntity':
        """
        Create an ATTDEF entity in the drawing database and add it to the block entity space.

        Args:
            tag (str): attribute name as string without spaces
            insert: attribute insert point relative to block origin (0, 0, 0)
            text (str): preset text for attribute

        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['tag'] = tag
        dxfattribs['insert'] = insert
        dxfattribs['text'] = text
        return self.build_and_add_entity('ATTDEF', dxfattribs)

    def attdefs(self) -> Iterable['DXFEntity']:
        """
        Iterate over all ATTDEF entities.

        """
        return (entity for entity in self if entity.dxftype() == 'ATTDEF')

    def has_attdef(self, tag: str) -> bool:
        """
        Check if ATTDEF for *tag* exists.

        Args:
            tag (str): tag name

        """
        return self.get_attdef(tag) is not None

    def get_attdef(self, tag: str) -> Optional['DXFEntity']:
        """
        Get attached ATTDEF entity by *tag*.

        Args:
            tag (str): tag name

        Returns:
            Attdef() object

        """
        for attdef in self.attdefs():
            if tag == attdef.dxf.tag:
                return attdef

    def get_attdef_text(self, tag: str, default: str = None) -> str:
        """
        Get content text of attached ATTDEF entity *tag*.

        Args:
            tag (str): tag name
            default (str): default value if tag is absent

        Returns:
            content text as str

        """
        attdef = self.get_attdef(tag)
        if attdef is None:
            return default
        return attdef.dxf.text

    # end of public interface

    def add_entity(self, entity: 'DXFEntity') -> None:
        """
        Add entity to the block entity space.

        """
        self.add_handle(entity.dxf.handle)
        entity.dxf.paperspace = 0  # set a model space, because paper space layout is a different class
        for linked_entity in entity.linked_entities():
            linked_entity.dxf.paperspace = 0

    def add_handle(self, handle: str) -> None:
        """
        Add entity by handle to the block entity space.

        """
        self._entity_space.append(handle)

    def write(self, tagwriter: 'TagWriter') -> None:
        def write_tags(handle):
            tags = self._entity_space.get_tags_by_handle(handle)
            tagwriter.write_tags(tags)

        write_tags(self._block_handle)
        self._entity_space.write(tagwriter)
        write_tags(self._endblk_handle)

    def delete_all_entities(self) -> None:
        # 1. delete from database
        for handle in self._entity_space:
            del self.entitydb[handle]
        # 2. delete from entity space
        self._entity_space.delete_all_entities()

    def destroy(self) -> None:
        self.delete_all_entities()
        del self.entitydb[self._block_handle]
        del self.entitydb[self._endblk_handle]

    def get_const_attdefs(self) -> Iterable['DXFEntity']:
        """
        Returns a generator for constant ATTDEF entities.

        """
        return (attdef for attdef in self.attdefs() if attdef.is_const)
