#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from ezdxf.lldxf import const
from .dxfentity import DXFTagStorage
from . import factory


@factory.register_entity
class ProxyEntity(DXFTagStorage):
    DXFTYPE = "ACAD_PROXY_ENTITY"

    def load_proxy_graphic(self) -> None:
        try:
            tags = self.xtags.get_subclass('AcDbProxyEntity')
        except const.DXFKeyError:
            return
        code: int = self.proxy_graphic_count_group_code()
        try:
            index = tags.tag_index(code)
        except const.DXFValueError:
            return
        binary_data = []
        for code, value in tags[index + 1:]:
            if code == 310:
                binary_data.append(value)
            else:
                break  # at first tag with group code != 310
        if len(binary_data):
            self.proxy_graphic = b''.join(binary_data)

    def proxy_graphic_count_group_code(self) -> int:
        # DXF reference says: 92
        # maybe different for different DXF versions
        return 160
