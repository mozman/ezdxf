# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, cast
from ezdxf.lldxf.const import DXFValueError, DXFKeyError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, ObjectsSection, DXFObject


class ObjectManager:
    def __init__(self, drawing: 'Drawing', dict_name: str = 'ACAD_MATERIAL', object_type: str = 'MATERIAL'):
        self.drawing = drawing
        self.object_type = object_type
        self.object_dict = drawing.rootdict.get_required_dict(dict_name)

    @property
    def objects(self) -> 'ObjectsSection':
        return self.drawing.objects

    def __iter__(self) -> Iterable['DXFObject']:
        wrap = self.drawing.dxffactory.wrap_handle
        for name, handle in self.object_dict.items():
            yield name, wrap(handle)

    def __len__(self) -> int:
        return len(self.object_dict)

    def __contains__(self, name: str) -> bool:
        return name in self.object_dict

    def get(self, name: str) -> 'DXFObject':
        """
        Get object by name.

        Args:
            name: object name as string

        Raises:
            DXFKeyError: if name does not exist

        """
        return self.object_dict.get_entity(name)

    def new(self, name: str) -> 'DXFObject':
        """
        Create a new object of type `self.object_type` and store its handle in the object manager dictionary.

        Args:
            name: name of new object as string

        Returns:
            new object of type `self.object_type`

        Raises:
            DXFValueError: if object name already exist

        """
        if name in self.object_dict:
            raise DXFValueError('{} entry {} already exists.'.format(self.object_type, name))
        return self._new(name, dxfattribs={'name': name})

    def _new(self, name: str, dxfattribs: dict) -> 'DXFObject':
        owner = self.object_dict.dxf.handle
        dxfattribs['owner'] = owner
        obj = self.objects.add_dxf_object_with_reactor(self.object_type, dxfattribs=dxfattribs)
        self.object_dict.add(name, obj.dxf.handle)
        return cast('DXFObject', obj)

    def delete(self, name: str) -> None:
        try:
            obj = self.object_dict.get_entity(name)
        except DXFKeyError:
            return
        else:
            self.object_dict.discard(name)
            self.objects.delete_entity(obj)

    def clear(self) -> None:
        """
        Delete all entries.

        """
        # destroy dxf entities (object manager is hard owner?)
        for name, obj in self:
            self.objects.delete_entity(obj)

        # delete all references
        self.object_dict.clear()
