#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Callable, Type
import abc

from . import sab, sat, const
from .abstract import DataLoader, AbstractEntity
from ezdxf.math import Matrix44, Vec3

Factory = Callable[[AbstractEntity], "AcisEntity"]

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

    def load(self, loader: DataLoader, entity_factory: Factory):
        pass

    def load_attrib(
        self,
        name: str,
        loader: DataLoader,
        entity_factory: Factory,
        expected_type: str = "",
    ):
        if not expected_type:
            expected_type = name
        entity = loader.read_ptr()
        if not entity.is_null_ptr:
            if entity.name == expected_type:
                setattr(self, name, entity_factory(entity))
            else:
                raise const.ParsingError(
                    f"expected entity type {expected_type}, got {entity.name}"
                )


@register
class Transform(AcisEntity):
    type: str = "transform"
    matrix = Matrix44()

    def load(self, loader: DataLoader, entity_factory: Factory):
        # Here comes an ugly hack, but SAT and SAB store the matrix data in a
        # quiet different way:
        if isinstance(loader, sat.SatDataLoader):
            # matrix values as 12 float values
            data = [loader.read_double() for _ in range(12)]
        else:
            # matrix values as a literal string
            values = loader.read_str().split(" ")
            if len(values) >= 12:
                data = [float(v) for v in values[:12]]
            else:
                data = [0.0] * 12
        data.insert(3, 0.0)
        data.insert(7, 0.0)
        data.insert(11, 0.0)
        data.append(1.0)
        self.matrix = Matrix44(data)


@register
class Body(AcisEntity):
    type: str = "body"
    lump: "Lump" = NULL_PTR  # type: ignore
    wire: "Wire" = NULL_PTR  # type: ignore
    transform: "Transform" = NULL_PTR  # type: ignore

    def load(self, loader: DataLoader, entity_factory: Factory):
        _ = loader.read_ptr()  # skip and ignore "Pattern"
        self.load_attrib("lump", loader, entity_factory)
        self.load_attrib("wire", loader, entity_factory)
        self.load_attrib("transform", loader, entity_factory)


@register
class Wire(AcisEntity):
    type: str = "wire"


@register
class Lump(AcisEntity):
    type: str = "lump"
    next_lump: "Lump" = NULL_PTR  # type: ignore
    body: "Body" = NULL_PTR  # type: ignore


class Loader(abc.ABC):
    def __init__(self, version: int):
        self.entities: Dict[int, AcisEntity] = {}
        self.version: int = version

    def get_entity(self, raw_entity: AbstractEntity) -> AcisEntity:
        uid = id(raw_entity)
        try:
            return self.entities[uid]
        except KeyError:
            entity = ENTITY_TYPES.get(raw_entity.name, AcisEntity)()
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
            entity = entity_factory(sab_entity)
            entity.id = sab_entity.id
            attributes = sab_entity.attributes
            if not attributes.is_null_ptr:
                entity.attributes = entity_factory(attributes)
            loader = sab.SabDataLoader(sab_entity.data, self.version)
            entity.load(loader, entity_factory)

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
            entity = entity_factory(sat_entity)
            entity.id = sat_entity.id
            attributes = sat_entity.attributes
            if not attributes.is_null_ptr:
                entity.attributes = entity_factory(attributes)
            loader = sat.SatDataLoader(sat_entity.data, self.version)
            entity.load(loader, entity_factory)

    @classmethod
    def load(cls, data: str) -> List[Body]:
        loader = cls(data)
        loader.load_entities()
        return loader.bodies()
