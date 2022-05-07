#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Union, List, Dict, Callable, Type, Any, Sequence
import abc

from . import sab, sat, const
from .const import Features
from .abstract import DataLoader, AbstractEntity, DataExporter
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

    @property
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
    ) -> None:
        if not expected_type:
            expected_type = name
        raw_entity = loader.read_ptr()
        if raw_entity.is_null_ptr:
            return
        if raw_entity.name.endswith(expected_type):
            setattr(self, name, entity_factory(raw_entity))
        else:
            raise const.ParsingError(
                f"expected entity type '{expected_type}', got '{raw_entity.name}'"
            )

    def export(self, exporter: DataExporter) -> None:
        raise const.ExportError(f"unsupported entity type: {self.type}")


@register
class Transform(AcisEntity):
    type: str = "transform"
    matrix = Matrix44()

    def load(self, loader: DataLoader, entity_factory: Factory):
        # Here comes an ugly hack, but SAT and SAB store the matrix data in a
        # quiet different way:
        if isinstance(loader, sab.SabDataLoader):
            # SAB matrix data is stored as a literal string and looks like a SAT
            # record: "1 0 0 0 1 0 0 0 1 0 0 0 1 no_rotate no_reflect no_shear"
            values = loader.read_str().split(" ")
            # delegate to SAT format:
            loader = sat.SatDataLoader(values, loader.version)
        data = [loader.read_double() for _ in range(12)]
        # insert values of the last matrix column (0, 0, 0, 1)
        data.insert(3, 0.0)
        data.insert(7, 0.0)
        data.insert(11, 0.0)
        data.append(1.0)
        self.matrix = Matrix44(data)


@register
class Body(AcisEntity):
    type: str = "body"
    pattern: "Pattern" = NULL_PTR  # type: ignore
    lump: "Lump" = NULL_PTR  # type: ignore
    wire: "Wire" = NULL_PTR  # type: ignore
    transform: "Transform" = NULL_PTR  # type: ignore

    def load(self, loader: DataLoader, entity_factory: Factory):
        if loader.version >= Features.PATTERN:
            self.load_attrib("pattern", loader, entity_factory)
        self.load_attrib("lump", loader, entity_factory)
        self.load_attrib("wire", loader, entity_factory)
        self.load_attrib("transform", loader, entity_factory)


@register
class Wire(AcisEntity):  # not implemented
    type: str = "wire"


@register
class Pattern(AcisEntity):  # not implemented
    type: str = "pattern"


@register
class Lump(AcisEntity):
    type: str = "lump"
    pattern: "Pattern" = NULL_PTR  # type: ignore
    next_lump: "Lump" = NULL_PTR  # type: ignore
    shell: "Shell" = NULL_PTR  # type: ignore
    body: "Body" = NULL_PTR  # type: ignore

    def load(self, loader: DataLoader, entity_factory: Factory):
        if loader.version >= Features.PATTERN:
            self.load_attrib("pattern", loader, entity_factory)
        self.load_attrib("next_lump", loader, entity_factory, "lump")
        self.load_attrib("shell", loader, entity_factory)
        self.load_attrib("body", loader, entity_factory)


@register
class Shell(AcisEntity):
    type: str = "shell"
    pattern: "Pattern" = NULL_PTR  # type: ignore
    next_shell: "Shell" = NULL_PTR  # type: ignore
    sub_shell: "Subshell" = NULL_PTR  # type: ignore
    face: "Face" = NULL_PTR  # type: ignore
    wire: "Wire" = NULL_PTR  # type: ignore
    lump: "Lump" = NULL_PTR  # type: ignore

    def load(self, loader: DataLoader, entity_factory: Factory):
        if loader.version >= Features.PATTERN:
            self.load_attrib("pattern", loader, entity_factory)
        self.load_attrib("next_shell", loader, entity_factory, "shell")
        self.load_attrib("subshell", loader, entity_factory)
        self.load_attrib("face", loader, entity_factory)
        self.load_attrib("wire", loader, entity_factory)
        self.load_attrib("lump", loader, entity_factory)


@register
class Subshell(AcisEntity):  # not implemented
    type: str = "subshell"


@register
class Face(AcisEntity):
    type: str = "face"
    pattern: "Pattern" = NULL_PTR  # type: ignore
    next_face: "Face" = NULL_PTR  # type: ignore
    loop: "Loop" = NULL_PTR  # type: ignore
    shell: "Shell" = NULL_PTR  # type: ignore
    subshell: "Subshell" = NULL_PTR  # type: ignore
    surface: "Surface" = NULL_PTR  # type: ignore
    sense = True  # True = reversed; False = forward
    double_sided = False  # True = double; False = single
    containment = False  # if double_sided: True = in, False = out

    def load(self, loader: DataLoader, entity_factory: Factory):
        if loader.version >= Features.PATTERN:
            self.load_attrib("pattern", loader, entity_factory)
        self.load_attrib("next_face", loader, entity_factory, "face")
        self.load_attrib("loop", loader, entity_factory)
        self.load_attrib("shell", loader, entity_factory)
        self.load_attrib("subshell", loader, entity_factory)
        self.load_attrib("surface", loader, entity_factory)
        self.sense = loader.read_bool("reversed", "forward")
        self.double_sided = loader.read_bool("double", "single")
        if self.double_sided:
            self.containment = loader.read_bool("in", "out")


@register
class Surface(AcisEntity):
    type: str = "surface"


@register
class PlaneSurface(Surface):
    type: str = "plane-surface"


class Loader(abc.ABC):
    records: Sequence[Union[sat.SatEntity, sab.SabEntity]]

    def __init__(self, version: int):
        self.entities: Dict[int, AcisEntity] = {}
        self.version: int = version

    def get_entity(self, raw_entity: AbstractEntity) -> AcisEntity:
        uid = id(raw_entity)
        try:
            return self.entities[uid]
        except KeyError:  # create a new entity
            entity = ENTITY_TYPES.get(raw_entity.name, AcisEntity)()
            self.entities[uid] = entity
            return entity

    def bodies(self) -> List[Body]:
        # noinspection PyTypeChecker
        return [e for e in self.entities.values() if isinstance(e, Body)]

    def load_entities(self):
        entity_factory = self.get_entity

        for raw_entity in self.records:
            entity = entity_factory(raw_entity)
            entity.id = raw_entity.id
            attributes = raw_entity.attributes
            if not attributes.is_null_ptr:
                entity.attributes = entity_factory(attributes)
            data_loader = self.make_data_loader(raw_entity.data)
            entity.load(data_loader, entity_factory)

    @abc.abstractmethod
    def make_data_loader(self, data: List[Any]) -> DataLoader:
        pass


class SabLoader(Loader):
    def __init__(self, data: bytes):
        builder = sab.parse_sab(data)
        super().__init__(builder.header.version)
        self.records = builder.entities

    def make_data_loader(self, data: List[Any]) -> DataLoader:
        return sab.SabDataLoader(data, self.version)

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

    def make_data_loader(self, data: List[Any]) -> DataLoader:
        return sat.SatDataLoader(data, self.version)

    @classmethod
    def load(cls, data: str) -> List[Body]:
        loader = cls(data)
        loader.load_entities()
        return loader.bodies()
