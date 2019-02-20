# Created: 21.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List
from ezdxf.lldxf.const import DXFKeyError, DXFValueError, DXFInternalEzdxfError
from ezdxf.lldxf.const import MODEL_SPACE_R2000, PAPER_SPACE_R2000, TMP_PAPER_SPACE_NAME
from ezdxf.lldxf.validator import is_valid_name
from .layout import Layout

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFEntity
    from ezdxf.entities.dictionary import Dictionary
    from ezdxf.drawing2 import Drawing


# todo DXF12: $MODEL_SPACE and $PAPER_SPACE
# rename $MODEL_SPACE -> *Model_Space at loading
# rename $PAPER_SPACE -> *Paper_Space at loading
# export *MODEL_SPACE as $Model_Space for DXF12
# export *PAPER_SPACE as $Paper_Space for DXF12


def _link_entities_section_into_blocks(doc: 'Drawing') -> None:
    """
    Link entity spaces from entities section into associated block layouts.

    """
    blocks = doc.blocks
    if '*MODEL_SPACE' in blocks:
        model_space_block = blocks.get('*MODEL_SPACE')
        model_space_block.set_entity_space(doc.entities.model_space_entities())
        active_layout_block = blocks.get('*PAPER_SPACE')
        active_layout_block.set_entity_space(doc.entities.active_layout_entities())
        doc.entities.clear()  # remove entities for entities section -> stored in blocks
    else:  # todo: no blocks for modelspace and paperspace found
        pass


class Layouts:
    def __init__(self, doc: 'Drawing'):
        """ Default constructor """
        self.doc = doc
        self._layouts = {}  # type: Dict[str, Layout]
        self._dxf_layouts = self.doc.rootdict['ACAD_LAYOUT']  # type: Dictionary # key: layout name; value: Layout()

    @classmethod
    def setup(cls, doc: 'Drawing'):
        """ Constructor from scratch """
        layouts = Layouts(doc)
        layouts.setup_modelspace()
        layouts.setup_paperspace()
        return layouts

    def setup_modelspace(self):
        self._new_special('Model', MODEL_SPACE_R2000, dxfattribs={'taborder': 0})

    def setup_paperspace(self):
        self._new_special('Layout1', PAPER_SPACE_R2000, dxfattribs={'taborder': 1})

    def _new_special(self, name: str, block_name: str, dxfattribs: dict) -> 'Layout':
        if name in self._layouts:
            raise DXFValueError('Layout "{}" already exists'.format(name))
        dxfattribs['owner'] = self._dxf_layouts.dxf.handle
        layout = Layout.new(name, block_name, self.doc, dxfattribs=dxfattribs)
        self._dxf_layouts[name] = layout
        self._layouts[name] = layout

        return layout

    def unique_paperspace_name(self) -> str:
        blocks = self.doc.blocks
        count = 0
        while "*Paper_Space%d" % count in blocks:
            count += 1
        return "*Paper_Space%d" % count

    def new(self, name: str, dxfattribs: dict = None) -> 'Layout':
        """
        Create a new Layout.

        Args:
            name (str): layout name as shown in tab
            dxfattribs (dict): DXF attributes for the ``LAYOUT`` entity

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

        self._dxf_layouts[name] = layout
        self._layouts[name] = layout

        return layout

    @classmethod
    def load(cls, doc: 'Drawing') -> 'Layouts':
        """ Constructor if loading from file. """
        _link_entities_section_into_blocks(doc)
        layouts = Layouts(doc)
        layouts.setup_from_rootdict()
        return layouts

    def setup_from_rootdict(self) -> None:
        for name, dxf_layout in self._dxf_layouts.items():
            self._layouts[name] = Layout(dxf_layout, self.doc)

    def __len__(self) -> int:
        """
        Returns layout count.

        """
        return len(self._layouts)

    def __contains__(self, name: str) -> bool:
        """
        Returns if layout `name` exists.

        Args:
            name str: layout name

        """
        return name in self._layouts

    def __iter__(self) -> Iterable['Layout']:
        return iter(self._layouts.values())

    def modelspace(self) -> 'Layout':
        """
        Get model space layout.

        Returns:
            Layout: model space layout

        """
        return self.get('Model')

    def names(self) -> Iterable[str]:
        """
        Returns all layout names.

        Returns:
            Iterable[str]: layout names

        """
        return self._layouts.keys()

    def get(self, name: str) -> 'Layout':
        """
        Get layout by name.

        Args:
            name (str): layout name as shown in tab, e.g. ``Model`` for model space

        Returns:
            Layout: layout

        """
        if name is None:
            first_layout_name = self.names_in_taborder()[1]
            return self._layouts[first_layout_name]
        else:
            return self._layouts[name]

    def rename(self, old_name: str, new_name: str) -> None:
        """
        Rename a layout. Layout ``Model`` can not renamed and the new name of a layout must not exist.

        Args:
            old_name (str): actual layout name
            new_name (str): new layout name

        """
        if old_name == 'Model':
            raise ValueError('Can not rename model space.')
        if new_name in self._layouts:
            raise ValueError('Layout "{}" already exists.'.format(new_name))

        layout = self._layouts[old_name]
        layout.rename(new_name)
        del self._layouts[old_name]
        self._layouts[new_name] = layout

    def names_in_taborder(self) -> List[str]:
        """
        Returns all layout names in tab order as a list of strings.

        """
        names = [(layout.dxf.taborder, name) for name, layout in self._layouts.items()]
        return [name for order, name in sorted(names)]

    def get_layout_for_entity(self, entity: 'DXFEntity') -> 'Layout':
        """
        Returns layout the `entity` resides in.

        Args:
            entity (DXFEntity): generic DXF entity

        """
        return self.get_layout_by_key(entity.dxf.owner)

    def get_layout_by_key(self, layout_key: str) -> 'Layout':
        """
        Returns a layout by its layout key.

        Args:
            layout_key (str): layout key

        """
        for layout in self._layouts.values():
            if layout_key == layout.layout_key:
                return layout
        raise DXFKeyError('Layout with key "{}" does not exist.'.format(layout_key))

    def get_active_layout_key(self):
        active_layout_block_record = self.doc.block_records.get(PAPER_SPACE_R2000)
        return active_layout_block_record.dxf.handle

    def set_active_layout(self, name: str) -> None:
        """
        Set active paper space layout.

        Args:
            name (str): layout name as shown in tab

        """
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
        """
        Delete layout `name` and all entities in it.

        Args:
            name (str): layout name as shown in tabs

        Raises:
            KeyError: if layout `name` do not exists
            ValueError: if `name` is ``Model`` (deleting model space)

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
        Returns active paper space layout.

        """
        for layout in self:
            if layout.is_active_paperspace:
                return layout
        raise DXFInternalEzdxfError('No active paper space found.')

    def export_entities_section(self, tagwriter: 'TagWriter')->None:
        """
        Write ``ENTITIES`` section to DXF file, the  ``ENTITIES`` section consist of all entities in model space and
        active paper space layout.

        All DXF entities of the remaining paper space layouts are stored in their associated ``BLOCK`` entity in the
        ``BLOCKS`` section.

        Args:
            tagwriter (TagWriter): tag writer object

        """
        self.modelspace().export_dxf(tagwriter)
        self.active_layout().export_dxf(tagwriter)
