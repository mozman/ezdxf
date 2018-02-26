# Created: 11.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .lldxf.types import cast_tag_value, DXFTag
from .lldxf.const import DXFStructureError, DXFInternalEzdxfError, DXFAttributeError, DXFInvalidLayerName
from .lldxf.const import DXFKeyError, DXFValueError
from .lldxf.validator import is_valid_layer_name


ACAD_REACTORS = '{ACAD_REACTORS'


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
    DXFATTRIBS = {}

    def __init__(self, tags, drawing=None):
        self.tags = tags
        self.dxf = DXFNamespace(self)  # all DXF attributes are accessible by the dxf attribute, like entity.dxf.handle
        self.drawing = drawing

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
            source: source layout, only for block layouts required

        """
        if source is None:
            try:
                source = self.drawing.layouts.get_layout_for_entity(self)
            except DXFKeyError:  # R2000+
                raise DXFValueError('Entity not in model space or paper space, specify block layout as source parameter.')
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
        return [key for key, attrib in self.DXFATTRIBS.items() if attrib.dxfversion is None or
                                                                  (attrib.dxfversion <= is_dxfversion)]

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
        # no subclass is subclass index 0
        try:
            subclass_tags = self.tags.subclasses[dxfattr.subclass]
        except IndexError:  # internal exception
            params = (self.dxftype(), self.tags.get_handle(), dxfattr.subclass)
            raise DXFInternalEzdxfError('Subclass index error in {} handle={} subclass={}.'.format(*params))

        if dxfattr.xtype is not None:
            return self._get_extented_type(subclass_tags, dxfattr.code, dxfattr.xtype)
        else:
            return subclass_tags.get_first_value(dxfattr.code)

    def has_dxf_default_value(self, key):
        """
        Returns True if the DXF attribute key has a DXF standard default value.

        """
        return self._get_dxfattr_definition(key).default is not None

    def set_dxf_attrib(self, key, value):
        dxfattr = self._get_dxfattr_definition(key)
        if dxfattr.dxfversion is not None and self.drawing is not None:
            if self.drawing.dxfversion < dxfattr.dxfversion:
                msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                raise DXFAttributeError(msg.format(key, self.drawing.dxfversion, dxfattr.dxfversion))
        # no subclass is subclass index 0
        subclasstags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            self._set_extended_type(subclasstags, dxfattr.code, dxfattr.xtype, value)
        else:
            subclasstags.set_first(dxfattr.code, cast_tag_value(dxfattr.code, value))

    def set_flag_state(self, flag, state=True, name='flags'):
        flags = self.get_dxf_attrib(name, 0)
        if state:
            flags = flags | flag
        else:
            flags = flags & ~flag
        self.set_dxf_attrib(name, flags)

    def get_flag_state(self, flag, name='flags'):
        return bool(self.get_dxf_attrib(name, 0) & flag)

    def del_dxf_attrib(self, key):
        dxfattr = self._get_dxfattr_definition(key)
        self._del_dxf_attrib(dxfattr)

    def clone_dxf_attribs(self):
        """
        Clones defined and existing DXF attributes as dict.

        """
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            value = self.get_dxf_attrib(key, default=None)
            if value is not None:
                dxfattribs[key] = value
        return dxfattribs

    def update_dxf_attribs(self, dxfattribs):
        for key, value in dxfattribs.items():
            self.set_dxf_attrib(key, value)

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
        value = cast_tag_value(code, value)
        vlen = len(value)
        if vlen == 3:
            if xtype == 'Point2D':
                raise DXFValueError('2 axis required')
        elif vlen == 2:
            if xtype == 'Point3D':
                raise DXFValueError('3 axis required')
        else:
            raise DXFValueError('2 or 3 axis required')
        tags.set_first(code, value)

    def _del_dxf_attrib(self, dxfattr):
        def point_codes(base_code):
            return base_code, base_code + 10, base_code + 20

        subclass_tags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            subclass_tags.remove_tags(codes=point_codes(dxfattr.code))
        else:
            subclass_tags.remove_tags(codes=(dxfattr.code,))

    def destroy(self):
        pass

    def has_app_data(self, appid):
        return self.tags.has_app_data(appid)

    def get_app_data(self, appid):
        return self.tags.get_app_data_content(appid)

    def set_app_data(self, appid, app_data_tags):
        if self.tags.has_app_data(appid):
            appdata = self.tags.get_app_data(appid)
            appdata[1:-1] = app_data_tags
        else:
            self.tags.new_app_data(appid, app_data_tags)

    def has_xdata(self, appid):
        return self.tags.has_xdata(appid)

    def get_xdata(self, appid):
        return self.tags.get_xdata(appid)[1:]  # without app id tag

    def set_xdata(self, appid, xdata_tags):
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

    def audit(self, auditor):
        """
        Audit entity for errors.

        Args:
            auditor: Audit() object

        """
        pass
