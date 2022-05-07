#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Union, Sequence, List, Dict, Callable
from . import sab

Factory = Callable[[int, str], "AcisEntity"]


class AcisEntity:
    type: str = "unsupported-entity"
    id: int
    attributes: "AcisEntity" = None

    def parse_sab(self, parser: sab.SabDataParser, factory: Factory):
        pass


class Body(AcisEntity):
    type: str = "body"


class Loader:
    def __init__(self):
        self.bodies: List[Body] = []
        self.sab_builder = sab.SabBuilder()
        self.entities: Dict[int, AcisEntity] = {}

    def parse_sab(self, data: Union[bytes, bytearray, Sequence[bytes]]):
        self.sab_builder = sab.parse_sab(data)

    def run(self):
        version = self.sab_builder.header.version
        factory = self.get_entity
        for index, sab_entity in enumerate(self.sab_builder.entities):
            entity = self.get_entity(index, sab_entity.name)
            entity.id = sab_entity.id
            attributes = sab_entity.attributes
            if not attributes.is_null_ptr:
                index = self.sab_builder.index(sab_entity)
                entity_type = sab_entity.name
                entity.attributes = self.get_entity(index, entity_type)
            args = sab.SabDataParser(sab_entity.data, version)
            entity.parse_sab(args, factory)

    def get_entity(self, index: int, entity_type: str):
        try:
            return self.entities[index]
        except KeyError:
            entity = ENTITY_TYPES.get(entity_type, AcisEntity)()
            self.entities[index] = entity
            return entity

    def set_bodies(self):
        self.bodies = [e for e in self.entities.values() if e.type == "body"]

    @classmethod
    def load_sab(cls, data: Union[bytes, bytearray, Sequence[bytes]]):
        loader = cls()
        loader.parse_sab(data)
        loader.run()
        loader.set_bodies()
        return loader


ENTITY_TYPES = {
    "body": Body,
}