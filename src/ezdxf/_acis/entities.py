#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Union, Sequence, List, Dict, Callable, Type
import abc
from . import sab, sat
from .abstract import AbstractBuilder, DataParser

Factory = Callable[[int, str], "AcisEntity"]

ENTITY_TYPES: Dict[str, Type["AcisEntity"]] = {}


def load(data: Union[str, bytes, bytearray]) -> List["Body"]:
    if isinstance(data, (bytes, bytearray)):
        loader = SabLoader.load(data)
    elif isinstance(data, str):
        loader = SatLoader.load(data)
    else:
        raise TypeError("invalid data type")
    return loader.bodies


def register(cls: Type["AcisEntity"]):
    ENTITY_TYPES[cls.type] = cls
    return cls


class AcisEntity:
    type: str = "unsupported-entity"
    id: int
    attributes: "AcisEntity" = None  # type: ignore

    def parse(self, parser: DataParser, entity_factory: Factory):
        pass


@register
class Body(AcisEntity):
    type: str = "body"


class Loader(abc.ABC):
    builder: AbstractBuilder

    def __init__(self):
        self.bodies: List[Body] = []
        self.entities: Dict[int, AcisEntity] = {}

    def get_version(self):
        return self.builder.header.version

    def get_entity(self, index: int, entity_type: str) -> AcisEntity:
        try:
            return self.entities[index]
        except KeyError:
            entity = ENTITY_TYPES.get(entity_type, AcisEntity)()
            self.entities[index] = entity
            return entity

    def set_bodies(self) -> None:
        self.bodies = [e for e in self.entities.values() if isinstance(e, Body)]

    def run(self):
        self.load_entities()
        self.set_bodies()

    @abc.abstractmethod
    def load_entities(self):
        pass


class SabLoader(Loader):
    def __init__(self, data: bytes):
        super().__init__()
        self.builder = sab.parse_sab(data)

    def load_entities(self):
        version = self.get_version()
        entity_factory = self.get_entity
        for index, sab_entity in enumerate(self.builder.entities):
            entity = entity_factory(index, sab_entity.name)
            entity.id = sab_entity.id
            attributes = sab_entity.attributes
            if not attributes.is_null_ptr:
                index = self.builder.index(sab_entity)
                entity_type = sab_entity.name
                entity.attributes = self.get_entity(index, entity_type)
            args = sab.SabDataParser(sab_entity.data, version)
            entity.parse(args, entity_factory)

    @classmethod
    def load(cls, data: Union[bytes, bytearray]):
        loader = cls(data)
        loader.run()
        return loader


class SatLoader(Loader):
    def __init__(self, data: str):
        super().__init__()
        self.builder = sat.parse_sat(data)

    def load_entities(self):
        version = self.get_version()
        entity_factory = self.get_entity
        for index, sat_entity in enumerate(self.builder.entities):
            entity = entity_factory(index, sat_entity.name)
            entity.id = sat_entity.id
            attributes = sat_entity.attributes
            if not attributes.is_null_ptr:
                index = self.builder.index(sat_entity)
                entity_type = sat_entity.name
                entity.attributes = self.get_entity(index, entity_type)
            args = sat.SatDataParser(sat_entity.data, version)
            entity.parse(args, entity_factory)

    @classmethod
    def load(cls, data: str):
        loader = cls(data)
        loader.run()
        return loader
