# Created: 21.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List
import logging
from ezdxf.lldxf.const import DXFKeyError, DXFValueError, DXFInternalEzdxfError, DXFTableEntryError
from ezdxf.lldxf.const import MODEL_SPACE_R2000, PAPER_SPACE_R2000, TMP_PAPER_SPACE_NAME
from ezdxf.lldxf.validator import is_valid_name
from .layout import Layout

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, Dictionary, Drawing, BlockRecord, DXFLayout

logger = logging.getLogger('ezdxf')


class Layouts:
    def __init__(self, doc: 'Drawing'):
        """ Default constructor. (internal API) """
        self.doc = doc
        self._layouts = {}  # type: Dict[str, Layout]
        self._dxf_layouts = self.doc.rootdict['ACAD_LAYOUT']  # type: Dictionary # key: layout name; value: Layout()

    @classmethod
    def setup(cls, doc: 'Drawing'):
        """ Constructor from scratch. (internal API) """
        layouts = Layouts(doc)
        layouts.setup_modelspace()
        layouts.setup_paperspace()
        return layouts

    def setup_modelspace(self):
        """ Modelspace setup. (internal API) """
        self._new_special('Model', MODEL_SPACE_R2000, dxfattribs={'taborder': 0})

    def setup_paperspace(self):
        """ First layout setup. (internal API) """
        self._new_special('Layout1', PAPER_SPACE_R2000, dxfattribs={'taborder': 1})

    def _new_special(self, name: str, block_name: str, dxfattribs: dict) -> 'Layout':
        if name in self._layouts:
            raise DXFValueError('Layout "{}" already exists'.format(name))
        dxfattribs['owner'] = self._dxf_layouts.dxf.handle
        layout = Layout.new(name, block_name, self.doc, dxfattribs=dxfattribs)
        self._dxf_layouts[name] = layout.dxf_layout
        self._layouts[name] = layout

        return layout

    def unique_paperspace_name(self) -> str:
        """ Returns a unique paperspace name. (internal API)"""
        blocks = self.doc.blocks
        count = 0
        while "*Paper_Space%d" % count in blocks:
            count += 1
        return "*Paper_Space%d" % count

    def new(self, name: str, dxfattribs: dict = None) -> 'Layout':
        """ Create a new :class:`~ezdxf.layouts.Layout`.

        Args:
            name: layout name as shown in tab
            dxfattribs: additional DXF attributes for the :class:`~ezdxf.entities.layout.DXFLayout` entity

        Raises:
            DXFValueError: Invalid characters in layout name.
            DXFValueError: Layout `name` already exist.

        """
        if not is_valid_name(name):
            raise DXFValueError('name contains invalid characters')

        if name in self._layouts:
            raise DXFValueError('Layout "{}" already exists'.format(name))

        dxfattribs = dict(dxfattribs or {})  # copy attribs
        dxfattribs['owner'] = self._dxf_layouts.dxf.handle
        dxfattribs.setdefault('taborder', len(self._layouts) + 1)
        block_name = self.unique_paperspace_name()
        layout = Layout.new(name, block_name, self.doc, dxfattribs=dxfattribs)

        self._dxf_layouts[name] = layout.dxf_layout
        self._layouts[name] = layout

        return layout

    @classmethod
    def load(cls, doc: 'Drawing') -> 'Layouts':
        """ Constructor if loading from file. (internal API) """
        layouts = cls(doc)
        layouts.setup_from_rootdict()

        # DXF R12: block/block_record for *Model_Space and *Paper_Space already exists
        if len(layouts) < 2:  # restore missing DXF Layouts
            layouts.restore('Model', MODEL_SPACE_R2000, taborder=0)
            layouts.restore('Layout1', PAPER_SPACE_R2000, taborder=1)

        # find orphaned LAYOUTS
        layout_names = (o.dxf.name for o in doc.objects if o.dxftype == 'LAYOUT')
        for layout_name in layout_names:
            if layout_name not in layouts:
                logger.debug('Found orphaned LAYOUT "{}"'.format(layout_name))

        # find orphaned BLOCK_RECORD *Paper_Space? entries
        psp_br_handles = {
            br.dxf.handle for br in doc.block_records if br.dxf.name.lower().startswith('*paper_space')
        }
        psp_layout_br_handles = {
            layout.dxf.block_record_handle for layout in layouts._layouts.values() if layout.dxf.name != 'Model'
        }
        mismatch = psp_br_handles.difference(psp_layout_br_handles)
        if len(mismatch):
            logger.debug(
                'Found {} layout(s) defined by BLOCK_RECORD entries without LAYOUT entity.'.format(len(mismatch)))

        return layouts

    def restore(self, name: str, block_record_name: str, taborder: int) -> None:
        """ Restore layout from block if DXFLayout do not exist. (internal API) """
        if name in self._layouts:
            return
        block_layout = self.doc.blocks.get(block_record_name)
        self._new_from_block_layout(name, block_layout, taborder)

    def _new_from_block_layout(self, name, block_layout, taborder: int) -> 'Layout':
        dxfattribs = {
            'owner': self._dxf_layouts.dxf.handle,
            'name': name,
            'block_record_handle': block_layout.block_record_handle,
            'taborder': taborder,
        }
        dxf_layout = self.doc.objects.new_entity('LAYOUT', dxfattribs=dxfattribs)
        layout = Layout.load(dxf_layout, self.doc)
        self._dxf_layouts[name] = layout.dxf_layout
        self._layouts[name] = layout
        return layout

    def setup_from_rootdict(self) -> None:
        """ Setup layout manger from root dictionary. (internal API) """
        for name, dxf_layout in self._dxf_layouts.items():
            self._layouts[name] = Layout(dxf_layout, self.doc)

    def __len__(self) -> int:
        """ Returns the count for layouts. """
        return len(self._layouts)

    def __contains__(self, name: str) -> bool:
        """ Returns ``True`` if layout `name` exist, support for the :code:`in` operator. """
        return name in self._layouts

    def __iter__(self) -> Iterable['Layout']:
        """ Iterate over modelspace layout and all paperspace layouts as :class:`~ezdxf.layouts.Layout` objects.
        """
        return iter(self._layouts.values())

    def modelspace(self) -> 'Layout':
        """ Returns the modelspace :class:`~ezdxf.layouts.Layout` object. """
        return self.get('Model')

    def names(self) -> Iterable[str]:
        """ Returns iterable of all layout names. """
        return self._layouts.keys()

    def get(self, name: str) -> 'Layout':
        """
        Get layout by `name``.

        Args:
            name: layout name as shown in tab, e.g. ``'Model'`` for model space

        """
        if name is None:
            first_layout_name = self.names_in_taborder()[1]
            return self._layouts[first_layout_name]
        else:
            return self._layouts[name]

    def rename(self, old_name: str, new_name: str) -> None:
        """ Rename a layout. Layout ``Model`` can not renamed and the new name of a layout must not exist.

        Args:
            old_name: actual layout name
            new_name: new layout name

        Raises:
            DXFValueError: try to rename ``'Model'``
            DXFValueError: Layout `new_name` already exist.
        """
        if old_name == 'Model':
            raise DXFValueError('Can not rename model space.')
        if new_name in self._layouts:
            raise DXFValueError('Layout "{}" already exist.'.format(new_name))

        layout = self._layouts[old_name]
        layout.rename(new_name)
        del self._layouts[old_name]
        self._layouts[new_name] = layout

    def names_in_taborder(self) -> List[str]:
        """ Returns all layout names in tab order as a list of strings. """
        names = [(layout.dxf.taborder, name) for name, layout in self._layouts.items()]
        return [name for order, name in sorted(names)]

    def get_layout_for_entity(self, entity: 'DXFEntity') -> 'Layout':
        """ Returns the owner layout for `entity`. """
        return self.get_layout_by_key(entity.dxf.owner)

    def get_layout_by_key(self, layout_key: str) -> 'Layout':
        """ Returns a layout by its `layout_key`. (internal API) """
        try:
            block_record = self.doc.entitydb[layout_key]
            dxf_layout = self.doc.entitydb[block_record.dxf.layout]
        except KeyError:
            raise DXFKeyError('Layout with key "{}" does not exist.'.format(layout_key))
        return self.get(dxf_layout.dxf.name)

    def get_active_layout_key(self):
        """ Returns layout kay for the active paperspace layout. (internal API) """
        active_layout_block_record = self.doc.block_records.get(PAPER_SPACE_R2000)
        return active_layout_block_record.dxf.handle

    def set_active_layout(self, name: str) -> None:
        """ Set layout `name` as active paperspace layout. """
        if name == 'Model':  # reserved layout name
            raise DXFValueError('Can not set model space as active layout')
        new_active_layout = self.get(name)  # raises KeyError if no layout 'name' exists
        old_active_layout_key = self.get_active_layout_key()
        if old_active_layout_key == new_active_layout.layout_key:
            return  # layout 'name' is already the active layout

        blocks = self.doc.blocks
        new_active_paper_space_name = new_active_layout.block_record_name

        blocks.rename_block(PAPER_SPACE_R2000, TMP_PAPER_SPACE_NAME)
        blocks.rename_block(new_active_paper_space_name, PAPER_SPACE_R2000)
        blocks.rename_block(TMP_PAPER_SPACE_NAME, new_active_paper_space_name)

    def delete(self, name: str) -> None:
        """ Delete layout `name` and all entities owned by it.

        Args:
            name (str): layout name as shown in tabs

        Raises:
            KeyError: if layout `name` do not exists
            ValueError: if `name` is ``'Model'`` (deleting modelspace)

        """
        if name == 'Model':
            raise DXFValueError("Can not delete model space layout.")

        layout = self._layouts[name]
        if layout.layout_key == self.get_active_layout_key():  # name is the active layout
            for layout_name in self.names():
                if layout_name not in (name, 'Model'):  # set any other layout as active layout
                    self.set_active_layout(layout_name)
                    break
        self._dxf_layouts.remove(layout.name)
        del self._layouts[layout.name]
        layout.destroy()

    def active_layout(self) -> 'Layout':
        """
        Returns the active paperspace layout.

        """
        for layout in self:
            if layout.is_active_paperspace:
                return layout
        raise DXFInternalEzdxfError('No active paper space found.')
