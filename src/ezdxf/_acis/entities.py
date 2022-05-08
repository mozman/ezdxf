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
INF = float("inf")


def load(data: Union[str, bytes, bytearray]) -> List["Body"]:
    if isinstance(data, (bytes, bytearray)):
        return SabLoader.load(data)
    elif isinstance(data, str):
        return SatLoader.load(data)
    raise TypeError(f"invalid type of data: {type(data)}")


def register(cls: Type["AcisEntity"]):
    ENTITY_TYPES[cls.type] = cls
    return cls


class NoneEntity:
    type: str = const.NONE_ENTITY_NAME

    @property
    def is_none(self) -> bool:
        return self.type == const.NONE_ENTITY_NAME


NONE_REF: Any = NoneEntity()


class AcisEntity(NoneEntity):
    type: str = "unsupported-entity"
    id: int
    attributes: "AcisEntity" = NONE_REF

    def load(self, loader: DataLoader, entity_factory: Factory) -> None:
        self.restore_common(loader, entity_factory)
        self.restore_data(loader)

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        pass

    def restore_data(self, loader: DataLoader) -> None:
        pass

    def export(self, exporter: DataExporter) -> None:
        self.write_common(exporter)
        self.write_data(exporter)

    def write_common(self, exporter: DataExporter) -> None:
        raise const.ExportError(f"unsupported entity type: {self.type}")

    def write_data(self, exporter: DataExporter) -> None:
        pass


def restore_entity(
    expected_type: str, loader: DataLoader, entity_factory: Factory
) -> Any:
    raw_entity = loader.read_ptr()
    if raw_entity.is_null_ptr:
        return NONE_REF
    if raw_entity.name.endswith(expected_type):
        return entity_factory(raw_entity)
    else:
        raise const.ParsingError(
            f"expected entity type '{expected_type}', got '{raw_entity.name}'"
        )


@register
class Transform(AcisEntity):
    type: str = "transform"
    matrix = Matrix44()

    def restore_data(self, loader: DataLoader) -> None:
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


class SupportsPattern(AcisEntity):
    pattern: "Pattern" = NONE_REF

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        if loader.version >= Features.PATTERN:
            self.pattern = restore_entity("pattern", loader, entity_factory)


@register
class Body(SupportsPattern):
    type: str = "body"
    pattern: "Pattern" = NONE_REF
    lump: "Lump" = NONE_REF
    wire: "Wire" = NONE_REF
    transform: "Transform" = NONE_REF

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        super().restore_common(loader, entity_factory)
        self.lump = restore_entity("lump", loader, entity_factory)
        self.wire = restore_entity("wire", loader, entity_factory)
        self.transform = restore_entity("transform", loader, entity_factory)


@register
class Wire(SupportsPattern):  # not implemented
    type: str = "wire"


@register
class Pattern(AcisEntity):  # not implemented
    type: str = "pattern"


@register
class Lump(SupportsPattern):
    type: str = "lump"
    next_lump: "Lump" = NONE_REF
    shell: "Shell" = NONE_REF
    body: "Body" = NONE_REF

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        super().restore_common(loader, entity_factory)
        self.next_lump = restore_entity("lump", loader, entity_factory)
        self.shell = restore_entity("shell", loader, entity_factory)
        self.body = restore_entity("body", loader, entity_factory)


@register
class Shell(SupportsPattern):
    type: str = "shell"
    next_shell: "Shell" = NONE_REF
    subshell: "Subshell" = NONE_REF
    face: "Face" = NONE_REF
    wire: "Wire" = NONE_REF
    lump: "Lump" = NONE_REF

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        super().restore_common(loader, entity_factory)
        self.next_shell = restore_entity("next_shell", loader, entity_factory)
        self.subshell = restore_entity("subshell", loader, entity_factory)
        self.face = restore_entity("face", loader, entity_factory)
        self.wire = restore_entity("wire", loader, entity_factory)
        self.lump = restore_entity("lump", loader, entity_factory)


@register
class Subshell(SupportsPattern):  # not implemented
    type: str = "subshell"


@register
class Face(SupportsPattern):
    type: str = "face"
    next_face: "Face" = NONE_REF
    loop: "Loop" = NONE_REF
    shell: "Shell" = NONE_REF
    subshell: "Subshell" = NONE_REF
    surface: "Surface" = NONE_REF
    sense = True  # True = reversed; False = forward
    double_sided = False  # True = double; False = single
    containment = False  # if double_sided: True = in, False = out

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        super().restore_common(loader, entity_factory)
        self.next_face = restore_entity("face", loader, entity_factory)
        self.loop = restore_entity("loop", loader, entity_factory)
        self.shell = restore_entity("shell", loader, entity_factory)
        self.subshell = restore_entity("subshell", loader, entity_factory)
        self.surface = restore_entity("surface", loader, entity_factory)
        self.sense = loader.read_bool("reversed", "forward")
        self.double_sided = loader.read_bool("double", "single")
        if self.double_sided:
            self.containment = loader.read_bool("in", "out")


@register
class Surface(SupportsPattern):
    type: str = "surface"
    u_bounds = INF, INF
    v_bounds = INF, INF

    def restore_data(self, loader: DataLoader) -> None:
        self.u_bounds = loader.read_interval(), loader.read_interval()
        self.v_bounds = loader.read_interval(), loader.read_interval()


@register
class Plane(Surface):
    type: str = "plane-surface"
    origin = Vec3(0, 0, 0)
    normal = Vec3(1, 0, 0)  # pointing outside
    u_dir = Vec3(1, 0, 0)  # unit vector!
    reversed_v = True  # True = reversed_v; False = forward_v

    def restore_common(
        self, loader: DataLoader, entity_factory: Factory
    ) -> None:
        super().restore_common(loader, entity_factory)
        self.origin = Vec3(loader.read_vec3())
        self.normal = Vec3(loader.read_vec3())
        self.u_dir = Vec3(loader.read_vec3())
        self.reversed_v = loader.read_bool("reversed_v", "forward_v")

    @property
    def v_dir(self):
        v_dir = self.normal.cross(self.u_dir)
        if self.reversed_v:
            return -v_dir
        return v_dir


@register
class Loop(SupportsPattern):
    type: str = "loop"


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