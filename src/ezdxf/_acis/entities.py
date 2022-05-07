#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Callable, Type
import abc

from . import sab, sat, const
from .abstract import DataParser
from ezdxf.math import Matrix44, Vec3

Factory = Callable[[int, str], "AcisEntity"]

ENTITY_TYPES: Dict[str, Type["AcisEntity"]] = {}


def load(data: Union[str, bytes, bytearray]) -> List["Body"]:
    if isinstance(data, (bytes, bytearray)):
        return SabLoader.load(data)
    elif isinstance(data, str):
        return SatLoader.load(data)
    raise TypeError(f"invalid type of data: {type(data)}")


def register(cls: Type["AcisEntity"]):
    ENTITY_TYPES[cls.type] = cls
    return cls


class NullPtr:
    type: str = const.NULL_PTR_NAME

    def is_null_ptr(self) -> bool:
        return self.type == const.NULL_PTR_NAME


NULL_PTR = NullPtr()


class AcisEntity(NullPtr):
    type: str = "unsupported-entity"
    id: int
    attributes: "AcisEntity" = NULL_PTR  # type: ignore

    def parse(self, parser: DataParser, entity_factory: Factory):
        pass


@register
class Transform(AcisEntity):
    type: str = "transform"
    matrix = Matrix44()

    def parse(self, parser: DataParser, entity_factory: Factory):
        # Here comes an ugly hack, but SAT and SAB store the matrix data in a
        # quiet different way:
        if isinstance(parser, sat.SatDataParser):
            self.matrix = Matrix44()
        else:
            self.matrix = Matrix44()


@register
class Body(AcisEntity):
    type: str = "body"
    transform: "Transform" = NULL_PTR  # type: ignore
    lump: "Lump" = NULL_PTR  # type: ignore

    def parse(self, parser: DataParser, entity_factory: Factory):
        pass


@register
class Lump(AcisEntity):
    type: str = "lump"
    next_lump: "Lump" = NULL_PTR  # type: ignore
    body: "Body" = NULL_PTR  # type: ignore


class Loader(abc.ABC):
    def __init__(self, version: int):
        self.entities: Dict[int, AcisEntity] = {}
        self.version: int = version

    def get_entity(self, uid: int, entity_type: str) -> AcisEntity:
        try:
            return self.entities[uid]
        except KeyError:
            entity = ENTITY_TYPES.get(entity_type, AcisEntity)()
            self.entities[uid] = entity
            return entity

    def bodies(self) -> List[Body]:
        return [e for e in self.entities.values() if isinstance(e, Body)]  # type: ignore

    @abc.abstractmethod
    def load_entities(self):
        pass


class SabLoader(Loader):
    def __init__(self, data: bytes):
        builder = sab.parse_sab(data)
        super().__init__(builder.header.version)
        self.records = builder.entities

    def load_entities(self):
        entity_factory = self.get_entity

        for sab_entity in self.records:
            entity = entity_factory(id(sab_entity), sab_entity.name)
            entity.id = sab_entity.id
            attributes = sab_entity.attributes
            if not attributes.is_null_ptr:
                entity.attributes = entity_factory(
                    id(sab_entity), sab_entity.name
                )
            args = sab.SabDataParser(sab_entity.data, self.version)
            entity.parse(args, entity_factory)

    @classmethod
    def load(cls, data: Union[bytes, bytearray]) -> List[Body]:
        loader = cls(data)
        loader.load_entities()
        return loader.bodies()


class SatLoader(Loader):
    def __init__(self, data: str):
        builder = sat.parse_sat(data)
        super().__init__(builder.header.version)
        self.records = builder.entities

    def load_entities(self):
        entity_factory = self.get_entity

        for sat_entity in self.records:
            entity = entity_factory(id(sat_entity), sat_entity.name)
            entity.id = sat_entity.id
            attributes = sat_entity.attributes
            if not attributes.is_null_ptr:
                entity.attributes = entity_factory(
                    id(sat_entity), sat_entity.name
                )
            args = sat.SatDataParser(sat_entity.data, self.version)
            entity.parse(args, entity_factory)

    @classmethod
    def load(cls, data: str) -> List[Body]:
        loader = cls(data)
        loader.load_entities()
        return loader.bodies()
