# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .lldxf.types import cast_tag_value, DXFTag, DXFVertex
from .lldxf.attributes import DXFCallback
from .lldxf.const import DXFStructureError, DXFInternalEzdxfError, DXFAttributeError, DXFInvalidLayerName
from .lldxf.const import DXFKeyError, DXFValueError
from .lldxf.validator import is_valid_layer_name
from .lldxf.tags import Tags, tuples2dxftags
from .tools import set_flag_state
from .algebra import OCS

ACAD_REACTORS = '{ACAD_REACTORS'
ACAD_XDICTIONARY = '{ACAD_XDICTIONARY'


class DXFNamespace(object):
    """
    Provides the dxf namespace for GenericWrapper.

    """
    __slots__ = ('_setter', '_getter', '_deleter')

    def __init__(self, wrapper):
        # DXFNamespace.__setattr__ can not set _getter and _setter
        super(DXFNamespace, self).__setattr__('_getter', wrapper.get_dxf_attrib)
        super(DXFNamespace, self).__setattr__('_setter', wrapper.set_dxf_attrib)
        super(DXFNamespace, self).__setattr__('_deleter', wrapper.del_dxf_attrib)

    def __getattr__(self, attrib):
        """
        Returns value of DXF attribute *attrib*. usage: value = DXFEntity.dxf.attrib

        """
        return self._getter(attrib)

    def __setattr__(self, attrib, value):
        """
        Set DXF attribute *attrib* to *value.  usage: DXFEntity.dxf.attrib = value

        """
        self._setter(attrib, value)

    def __delattr__(self, attrib):
        """
        Remove DXF attribute *attrib*.  usage: del DXFEntity.dxf.attrib

        """
        self._deleter(attrib)


class DXFEntity(object):
    TEMPLATE = None
    CLASS = None
    DXFATTRIBS = {}

    def __init__(self, tags, drawing=None):
        self.tags = tags
        self.dxf = DXFNamespace(self)  # all DXF attributes are accessible by the dxf attribute, like entity.dxf.handle
        self.drawing = drawing

    def __str__(self):
        return "{}(#{})".format(self.dxftype(), self.dxf.handle)

    def __repr__(self):
        return str(self.__class__) + " " + self.__str__()

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

    @classmethod
    def new(cls, handle, dxfattribs=None, drawing=None):
        if cls.TEMPLATE is None:
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(cls.TEMPLATE.clone(), drawing)
        entity.dxf.handle = handle
        if dxfattribs is not None:
            if 'layer' in dxfattribs:
                layer_name = dxfattribs['layer']
                if not is_valid_layer_name(layer_name):
                    raise DXFInvalidLayerName("Invalid layer name '{}'".format(layer_name))
            entity.update_dxf_attribs(dxfattribs)
        entity.post_new_hook()
        return entity

    def post_new_hook(self):
        """
        Called after entity creation.

        """
        pass

    def _new_entity(self, type_, dxfattribs):
        """
        Create new entity with same layout settings as *self*.

        Used by INSERT & POLYLINE to create appended DXF entities, don't use it to create new standalone entities.

        """
        entity = self.dxffactory.create_db_entry(type_, dxfattribs)
        self.dxffactory.copy_layout(self, entity)
        return entity

    def __copy__(self):
        """
        Deep copy of DXFEntity with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND).
        The new entity is not included in any layout space, so the owner tag is set to '0' for undefined owner/layout.

        Use Layout.add_entity(new_entity) to add the duplicated entity to a layout, layout can be the model space,
        a paper space layout or a block layout.

        It is not called __deepcopy__, because this is not a deep copy in the meaning of Python, because handle, link
        and owner is changed.

        """
        new_tags = self.entitydb.duplicate_tags(self.tags)
        entity = self.dxffactory.wrap_entity(new_tags)
        if self.supports_dxf_attrib('owner'):  # R2000+
            entity.dxf.owner = '0'  # reset ownership/layout
        return entity
    copy = __copy__

    def linked_entities(self):
        """
        Iterate over all linked entities, only POLYLINE and INSERT has linked entities (VERTEX, ATTRIB, SEQEND)

        Yields: DXFEntity() objects

        """
        link = self.tags.link
        wrap = self.dxffactory.wrap_handle
        while link is not None:
            entity = wrap(link)
            yield entity
            link = entity.tags.link

    def copy_to_layout(self, layout):
        """
        Copy entity to another layout.

        Args:
            layout: any layout (model space, paper space, block)

        Returns: new created entity as DXFEntity() object

        """
        new_entity = self.copy()
        layout.add_entity(new_entity)
        return new_entity

    def move_to_layout(self, layout, source=None):
        """
        Move entity from model space or a paper space layout to another layout. For block layout as source, the
        block layout has to be specified.

        Args:
            layout: any layout (model space, paper space, block)
            source: provide source layout, faster for DXF R12 and entity is in a block layout

        """
        if source is None:
            source = self.get_layout()
            if source is None:
                raise DXFValueError('Source layout for entity not found.')
        source.move_to_layout(self, layout)

    def dxftype(self):
        return self.tags.noclass[0].value

    def supports_dxf_attrib(self, key):
        """
        Returns True if DXF attribute key is supported else False. Does not grant that attribute key really exists.

        """
        dxfattr = self.DXFATTRIBS.get(key, None)
        if dxfattr is None:
            return False
        if dxfattr.dxfversion is None or self.drawing is None:
            return True
        return self.drawing.dxfversion >= dxfattr.dxfversion

    def valid_dxf_attrib_names(self):
        """
        Returns a list of supported DXF attribute names.

        """
        is_dxfversion = None if self.drawing is None else self.drawing.dxfversion
        return [key for key, attrib in self.DXFATTRIBS.items() if attrib.dxfversion is None or (attrib.dxfversion <= is_dxfversion)]

    def dxf_attrib_exists(self, key):
        """
        Returns True if DXF attrib key really exists else False. Raises AttributeError if key isn't supported.

        """
        # attributes with default values don't raise an exception!
        return self.get_dxf_attrib(key, default=None) is not None

    def _get_dxfattr_definition(self, key):
        try:
            return self.DXFATTRIBS[key]
        except KeyError:
            raise DXFAttributeError(key)

    def get_dxf_attrib(self, key, default=DXFValueError):
        dxfattr = self._get_dxfattr_definition(key)
        if isinstance(dxfattr, DXFCallback):
            return getattr(self, dxfattr.getter)()
        try:  # No check if attribute is valid for DXF version of drawing, if it is there you get it
            return self._get_dxf_attrib(dxfattr)
        except DXFValueError:
            if default is DXFValueError:
                # no DXF default values if DXF version is incorrect
                if dxfattr.dxfversion is not None and \
                        self.drawing is not None and \
                        self.drawing.dxfversion < dxfattr.dxfversion:
                    msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                    raise DXFValueError(msg.format(key, self.drawing.dxfversion, dxfattr.dxfversion))
                result = dxfattr.default  # default value defined by DXF specs
                if result is not None:
                    return result
                else:
                    raise DXFValueError("DXFAttrib '%s' does not exist." % key)
            else:
                return default

    def get_dxf_default_value(self, key):
        """
        Returns the default value as defined in the DXF standard.

        """
        return self._get_dxfattr_definition(key).default

    def _get_dxf_attrib(self, dxfattr):
        subclass_tags = self._get_dxf_attrib_subclass_tags(dxfattr.subclass)
        if dxfattr.xtype is not None:
            return self._get_extented_type(subclass_tags, dxfattr.code, dxfattr.xtype)
        else:
            return subclass_tags.get_first_value(dxfattr.code)

    def _get_dxf_attrib_subclass_tags(self, subclass_key):
        try:  # fast access subclass by index as int
            # no subclass is subclass index 0
            return self.tags.subclasses[subclass_key]
        except IndexError:
            raise DXFInternalEzdxfError('Subclass index error in {entity} subclass={index}.'.format(
                entity=self.__str__(),
                index=subclass_key,
            ))
        except TypeError:  # slow access subclass by name as string
            # raises DXFKeyError if subclass does not exist
            return self.tags.get_subclass(subclass_key)

    @staticmethod
    def _get_extented_type(tags, code, xtype):
        value = tags.get_first_value(code)
        if len(value) == 3:
            if xtype == 'Point2D':
                raise DXFStructureError("expected 2D point but found 3D point")
        elif xtype == 'Point3D':  # len(value) == 2
            raise DXFStructureError("expected 3D point but found 2D point")
        return value

    @staticmethod
    def _set_extended_type(tags, code, xtype, value):
        value = tuple(value)
        vlen = len(value)
        if vlen == 3:
            if xtype == 'Point2D':
                raise DXFValueError('2 axis required')
        elif vlen == 2:
            if xtype == 'Point3D':
                raise DXFValueError('3 axis required')
        else:
            raise DXFValueError('2 or 3 axis required')
        tags.set_first(DXFVertex(code, value))

    def has_dxf_default_value(self, key):
        """
        Returns True if the DXF attribute key has a DXF standard default value.

        """
        return self._get_dxfattr_definition(key).default is not None

    def set_dxf_attrib(self, key, value):
        dxfattr = self._get_dxfattr_definition(key)
        if isinstance(dxfattr, DXFCallback):
            if dxfattr.setter is None:
                raise DXFAttributeError("DXFAttrib '{}' is read only.".format(key))
            else:
                getattr(self, dxfattr.setter)(value)
                return
        if dxfattr.dxfversion is not None and self.drawing is not None:
            if self.drawing.dxfversion < dxfattr.dxfversion:
                msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                raise DXFAttributeError(msg.format(key, self.drawing.dxfversion, dxfattr.dxfversion))
        subclass_tags = self._get_dxf_attrib_subclass_tags(dxfattr.subclass)
        if dxfattr.xtype is not None:
            self._set_extended_type(subclass_tags, dxfattr.code, dxfattr.xtype, value)
        else:
            subclass_tags.set_first(DXFTag(dxfattr.code, cast_tag_value(dxfattr.code, value)))

    def del_dxf_attrib(self, key):
        dxfattr = self._get_dxfattr_definition(key)
        self._del_dxf_attrib(dxfattr)

    def _del_dxf_attrib(self, dxfattr):
        def point_codes(base_code):
            return base_code, base_code + 10, base_code + 20

        subclass_tags = self._get_dxf_attrib_subclass_tags(dxfattr.subclass)
        if dxfattr.xtype is not None:
            subclass_tags.remove_tags(codes=point_codes(dxfattr.code))
        else:
            subclass_tags.remove_tags(codes=(dxfattr.code,))

    def dxfattribs(self):
        """
        Clones defined and existing DXF attributes as dict.

        """
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            value = self.get_dxf_attrib(key, default=None)
            if value is not None:
                dxfattribs[key] = value
        return dxfattribs

    clone_dxf_attribs = dxfattribs

    def update_dxf_attribs(self, dxfattribs):
        for key, value in dxfattribs.items():
            self.set_dxf_attrib(key, value)

    def set_flag_state(self, flag, state=True, name='flags'):
        flags = self.get_dxf_attrib(name, 0)
        self.set_dxf_attrib(name, set_flag_state(flags, flag, state=state))

    def get_flag_state(self, flag, name='flags'):
        return bool(self.get_dxf_attrib(name, 0) & flag)

    def ocs(self):
        extrusion = self.get_dxf_attrib('extrusion', default=(0, 0, 1))
        return OCS(extrusion)

    def destroy(self):
        if self.has_extension_dict():
            xdict = self.get_extension_dict()
            self.drawing.objects.delete_entity(xdict)

    def has_app_data(self, appid):
        return self.tags.has_app_data(appid)

    def get_app_data(self, appid):
        return self.tags.get_app_data_content(appid)

    def set_app_data(self, appid, app_data_tags):
        app_data_tags = tuples2dxftags(app_data_tags)
        if self.tags.has_app_data(appid):
            appdata = self.tags.get_app_data(appid)
            appdata[1:-1] = app_data_tags
        else:
            self.tags.new_app_data(appid, app_data_tags)

    def has_xdata(self, appid):
        return self.tags.has_xdata(appid)

    def get_xdata(self, appid):
        return Tags(self.tags.get_xdata(appid)[1:])  # without app id tag

    def set_xdata(self, appid, xdata_tags):
        xdata_tags = tuples2dxftags(xdata_tags)
        if self.tags.has_xdata(appid):
            xdata = self.tags.get_xdata(appid)
            xdata[1:] = xdata_tags
        else:
            self.tags.new_xdata(appid, xdata_tags)

    def has_reactors(self):
        return self.has_app_data(ACAD_REACTORS)

    def get_reactors(self):
        reactor_tags = self.get_app_data(ACAD_REACTORS)
        return [tag.value for tag in reactor_tags]

    def set_reactors(self, reactor_handles):
        reactor_tags = [DXFTag(330, handle) for handle in reactor_handles]
        self.set_app_data(ACAD_REACTORS, reactor_tags)

    def append_reactor_handle(self, handle):
        reactors = set(self.get_reactors())
        reactors.add(handle)
        self.set_reactors(sorted(reactors, key=lambda x: int(x, base=16)))

    def remove_reactor_handle(self, handle):
        reactors = set(self.get_reactors())
        reactors.discard(handle)
        self.set_reactors(reactors)

    def has_extension_dict(self):
        return self.has_app_data(ACAD_XDICTIONARY)

    def get_extension_dict(self):
        """
        Get associated extension dictionary as DXFDictionary() object.

        """
        app_data = self.get_app_data(ACAD_XDICTIONARY)
        if len(app_data) == 0 or app_data[0].code != 360:
            raise DXFStructureError("XDICTIONARY error in entity: "+self.__str__())
        # are more than one XDICTIONARY possible?
        xdict_handle = app_data[0].value
        return self.dxffactory.wrap_handle(xdict_handle)

    def new_extension_dict(self):
        """
        Creates and assigns a new extensions dictionary. Link to an existing extension dictionary will be lost.

        """
        xdict = self.drawing.objects.add_dictionary(owner=self.dxf.handle)
        self.set_app_data(ACAD_XDICTIONARY, [DXFTag(360, xdict.dxf.handle)])
        return xdict

    def get_layout(self):
        return self.dxffactory.get_layout_for_entity(self)

    def audit(self, auditor):
        """
        Audit entity for errors.

        Args:
            auditor: Audit() object

        """
        pass
