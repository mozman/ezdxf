from typing import Any, TYPE_CHECKING, Tuple
from ezdxf.modern.tableentries import DimStyle  # DimStyle for DXF R2000 and later
from ezdxf.modern.tableentries import get_block_name_by_handle
from ezdxf.lldxf.const import DXFAttributeError
from ezdxf.render.arrows import ARROWS
import logging

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Dimension


class DimStyleOverride:
    def __init__(self, dimension: 'Dimension', override: dict = None):
        self.dimension = dimension
        dim_style_name = dimension.get_dxf_attrib('dimstyle', 'STANDARD')
        self.dim_style = self.drawing.dimstyles.get(dim_style_name)
        self.dxfattribs = self.get_dstyle_dict()
        self.update(override or {})

    @property
    def drawing(self):
        return self.dimension.drawing

    @property
    def dxfversion(self):
        return self.dimension.drawing.dxfversion

    def check_valid_attrib(self, name):
        if name not in DimStyle.DXFATTRIBS:
            raise DXFAttributeError('Invalid DXF attribute "{}" for DIMSTYLE.'.format(name))

    def get_dstyle_dict(self) -> dict:
        return self.dimension.get_acad_dstyle(self.dim_style)

    def get(self, attribute: str, default: Any = None) -> Any:
        if attribute in self.dxfattribs:
            result = self.dxfattribs[attribute]
        else:
            # Return default value for attributes not supported by DXF R12.
            # This is a hack to use the same algorithm to render DXF R2000 and DXF R12 DIMENSION entities.
            # But the DXF R2000 attributes are not stored in the DXF R12 file!!!
            try:
                result = self.dim_style.get_dxf_attrib(attribute, default)
            except DXFAttributeError:
                self.check_valid_attrib(attribute)
                # return default value for DXF R12 if valid DXF R2000 attribute
                result = default
        return result

    def update(self, attribs: dict) -> None:
        for key, value in attribs.items():
            self.check_valid_attrib(key)
            self.dxfattribs[key] = value

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.check_valid_attrib(key)
        self.dxfattribs[key] = value

    def __delitem__(self, key):
        self.check_valid_attrib(key)
        try:
            del self.dxfattribs[key]
        except KeyError:  # silent discard
            pass

    def commit(self) -> None:
        def set_arrow_handle(attrib_name, block_name):
            attrib_name += '_handle'
            if block_name in ARROWS:  # create all arrows on demand
                block_name = ARROWS.create_block(blocks, block_name)
            if block_name == '_CLOSEDFILLED':  # special arrow
                handle = '0'  # set special #0 handle for closed filled arrow
            else:
                block = blocks.get(block_name)
                handle = block.block_record_handle
            self.dxfattribs[attrib_name] = handle

        def set_linetype_handle(attrib_name, linetype_name):
            ltype = self.drawing.linetypes.get(linetype_name)
            self.dxfattribs[attrib_name + '_handle'] = ltype.dxf.handle

        if self.drawing.dxfversion > 'AC1009':
            # transform block names into block record handles
            blocks = self.drawing.blocks
            for attrib_name in ('dimblk', 'dimblk1', 'dimblk2', 'dimldrblk'):
                try:
                    block_name = self.dxfattribs.pop(attrib_name)
                except KeyError:
                    pass
                else:
                    set_arrow_handle(attrib_name, block_name)

        if self.drawing.dxfversion >= 'AC1021':
            # transform linetype names into LTYPE entry handles
            for attrib_name in ('dimltype', 'dimltex1', 'dimltex2'):
                try:
                    linetype_name = self.dxfattribs.pop(attrib_name)
                except KeyError:
                    pass
                else:
                    set_linetype_handle(attrib_name, linetype_name)

        self.dimension.set_acad_dstyle(self.dxfattribs, DimStyle)

    def set_arrows(self, blk: str = None, blk1: str = None, blk2: str = None, ldrblk: str = None):
        def set_arrow(dimvar: str, name: str) -> None:
            self.dxfattribs[dimvar] = name

        if blk is not None:
            set_arrow('dimblk', blk)
        if blk1 is not None:
            set_arrow('dimblk1', blk1)
        if blk2 is not None:
            set_arrow('dimblk2', blk2)
        if ldrblk is not None:
            set_arrow('dimldrblk', ldrblk)

    def get_arrow_names(self) -> Tuple[str, str]:
        dimtsz = self.get('dimtsz')
        blk1, blk2 = None, None
        if dimtsz == 0.:
            if bool(self.get('dimsah')):
                blk1 = self.get('dimblk1')
                blk2 = self.get('dimblk2')
            else:
                blk = self.get('dimblk')
                blk1 = blk
                blk2 = blk
        return blk1, blk2
