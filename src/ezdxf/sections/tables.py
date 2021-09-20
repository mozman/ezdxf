# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
import logging
from ezdxf.lldxf.const import DXFStructureError, DXF12
from .table import (
    Table,
    ViewportTable,
    StyleTable,
    LayerTable,
    LineTypeTable,
    AppIDTable,
    ViewTable,
    BlockRecordTable,
    DimStyleTable,
    UCSTable,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        Drawing,
        DXFEntity,
        DXFTagStorage,
        DimStyle,
    )

logger = logging.getLogger("ezdxf")

TABLENAMES = {
    "LAYER": "layers",
    "LTYPE": "linetypes",
    "APPID": "appids",
    "DIMSTYLE": "dimstyles",
    "STYLE": "styles",
    "UCS": "ucs",
    "VIEW": "views",
    "VPORT": "viewports",
    "BLOCK_RECORD": "block_records",
}

TABLESMAP = {
    "LAYER": LayerTable,
    "LTYPE": LineTypeTable,
    "STYLE": StyleTable,
    "DIMSTYLE": DimStyleTable,
    "VPORT": ViewportTable,
    "VIEW": ViewTable,
    "UCS": UCSTable,
    "APPID": AppIDTable,
    "BLOCK_RECORD": BlockRecordTable,
}


class TablesSection:
    def __init__(self, doc: "Drawing", entities: List["DXFEntity"] = None):
        assert doc is not None
        self.doc = doc
        # In the end all tables are not None and using "Optional" is awful!
        self.layers: LayerTable = None  # type: ignore
        self.linetypes: LineTypeTable = None  # type: ignore
        self.appids: AppIDTable = None  # type: ignore
        self.dimstyles: DimStyleTable = None  # type: ignore
        self.styles: StyleTable = None  # type: ignore
        self.ucs: UCSTable = None  # type: ignore
        self.views: ViewTable = None  # type: ignore
        self.viewports: ViewportTable = None  # type: ignore
        self.block_records: BlockRecordTable = None  # type: ignore

        if entities is not None:
            self._load(entities)
        self._create_missing_tables()
        # An this time all tables are not None!

    def _load(self, entities: List["DXFEntity"]) -> None:
        section_head: "DXFTagStorage" = entities[0]  # type: ignore
        if section_head.dxftype() != "SECTION" or section_head.base_class[
            1
        ] != (2, "TABLES"):
            raise DXFStructureError(
                "Critical structure error in TABLES section."
            )
        del entities[0]  # delete first entity (0, SECTION)

        table_records: List["DXFEntity"] = []
        table_name = None
        for entity in entities:
            if entity.dxftype() == "TABLE":
                if len(table_records):
                    # TABLE entity without preceding ENDTAB entity, should we care?
                    logger.debug(
                        'Ignore missing ENDTAB entity in table "{}".'.format(
                            table_name
                        )
                    )
                    self._load_table(table_name, table_records)  # type: ignore
                table_name = entity.dxf.name
                table_records = [entity]  # collect table head
            elif entity.dxftype() == "ENDTAB":  # do not collect (0, 'ENDTAB')
                self._load_table(table_name, table_records)  # type: ignore
                table_records = (
                    []
                )  # collect entities outside of tables, but ignore it
            else:  # collect table entries
                table_records.append(entity)

        if len(table_records):
            # last ENDTAB entity is missing, should we care?
            logger.debug(
                'Ignore missing ENDTAB entity in table "{}".'.format(table_name)
            )
            self._load_table(table_name, table_records)  # type: ignore

    def _load_table(
        self, name: str, table_entities: Iterable["DXFEntity"]
    ) -> None:
        """
        Load table from tags.

        Args:
            name: table name e.g. VPORT
            table_entities: iterable of table records

        """
        table_class = TABLESMAP[name]
        new_table = table_class(self.doc, table_entities)
        setattr(self, TABLENAMES[name], new_table)

    def _create_missing_tables(self) -> None:
        for record_name, table_name in TABLENAMES.items():
            if getattr(self, table_name) is None:
                self._create_new_table(record_name, table_name)

    def _create_new_table(self, record_name: str, table_name: str) -> None:
        """
        Setup new empty table.

        Args:
            record_name: table name e.g. VPORT
            table_name: TableSection attribute name e.g. viewports

        """
        handle = self.doc.entitydb.next_handle()
        table_class = TABLESMAP[record_name]
        table = table_class.new_table(record_name, handle, self.doc)
        setattr(self, table_name, table)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nTABLES\n")
        version = tagwriter.dxfversion
        self.viewports.export_dxf(tagwriter)
        self.linetypes.export_dxf(tagwriter)
        self.layers.export_dxf(tagwriter)
        self.styles.export_dxf(tagwriter)
        self.views.export_dxf(tagwriter)
        self.ucs.export_dxf(tagwriter)
        self.appids.export_dxf(tagwriter)
        self.dimstyles.export_dxf(tagwriter)
        if version > DXF12:
            self.block_records.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def create_table_handles(self):
        # DXF R12: TABLE does not require a handle and owner tag
        # DXF R2000+: TABLE requires a handle and an owner tag
        for name in TABLENAMES.values():
            table = getattr(self, name.lower())
            handle = self.doc.entitydb.next_handle()
            table.set_handle(handle)
