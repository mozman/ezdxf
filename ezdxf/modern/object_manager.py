# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.const import DXFValueError, DXFKeyError


class ObjectManager(object):
    def __init__(self, drawing, dict_name='ACAD_MATERIAL', object_type='MATERIAL'):
        self.drawing = drawing
        self.object_type = object_type
        self.object_dict = drawing.rootdict.get_required_dict(dict_name)

    @property
    def objects(self):
        return self.drawing.objects

    def __iter__(self):
        wrap = self.drawing.dxffactory.wrap_handle
        for name, handle in self.object_dict.items():
            yield name, wrap(handle)

    def __len__(self):
        return len(self.object_dict)

    def __contains__(self, name):
        return name in self.object_dict

    def get(self, name):
        """
        Get object by name.

        Args:
            name: object name as string

        Returns: DXF object

        Raises: DXFKeyError() if name does not exist

        """
        return self.object_dict.get_entity(name)

    def new(self, name):
        """
        Create a new object of type object_type and put it into the object manager dictionary.

        Args:
            name: name of new object as string

        Returns: new object of type object_type

        Raises: DXFValueError() if object name already exist

        """
        if name in self.object_dict:
            raise DXFValueError('{} entry {} already exists.'.format(self.object_type, name))
        return self._new(name, dxfattribs={'name': name})

    def _new(self, name, dxfattribs):
        owner = self.object_dict.dxf.handle
        dxfattribs['owner'] = owner
        obj = self.objects.add_dxf_object_with_reactor(self.object_type, dxfattribs=dxfattribs)
        self.object_dict.add(name, obj.dxf.handle)
        return obj

    def delete(self, name):
        try:
            obj = self.object_dict.get_entity(name)
        except DXFKeyError:
            return
        else:
            self.object_dict.discard(name)
            self.objects.delete_entity(obj)

    def clear(self):
        """
        Delete all entries.
        """
        for name, obj in self:  # destroy dxf group entities
            self.objects.delete_entity(obj)
        self.object_dict.clear()  # delete all group references
