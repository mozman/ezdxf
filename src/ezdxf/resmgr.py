#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from typing import TYPE_CHECKING, Dict, List, Iterator, cast, Callable, Iterable
from typing_extensions import Protocol, runtime_checkable
import abc

if TYPE_CHECKING:
    from ezdxf.entities import DXFEntity
    from ezdxf.document import Drawing

__all__ = ["ResourcePackage", "ResourceTransferManager"]


class ResourcePackage(abc.ABC):
    """A DXFEntity stores all required resources which are stored in the owner
    document as real Python references in the resource Package (not layer or
    linetype names ...).

    The TransferManager creates the required resources in the target document
    and replaces the stored Python object by the new created object and calls
    DXFEntity.load_resources(...), so the entity can update its reference or
    remove resources which can not be transferred.

    """

    @abc.abstractmethod
    def push(self, resources: List["DXFEntity"]):
        ...

    @abc.abstractmethod
    def pop(self) -> List["DXFEntity"]:
        ...


"""
Extension dictionaries: handled in DXFEntity.copy() and factory.bind()

Handles in XDATA?
Block references?

class DXFEntity:
    def dump_resources(self, package: ResourcePackage):
        package.push(self.get_entities_in_xdata())

    def get_entities_in_xdata(self):
        # in order of appearance
        # 1. 1005 -> 1. entity.dxf.handle
        # 2. 1003 -> 2. layer.dxf.name
        # 3. 1005 -> 3. entity.dxf.handle
        return []
    
    def put_entities_in_xdata(self, entities):
        for e in entities:
            pass
            # 1. 1005 <- 1. entity.dxf.handle
            # 2. 1003 <- 2. layer.dxf.name
            # 3. 1005 <- 3. entity.dxf.handle

    def load_resources(self, package: ResourcePackage):
        xdata = package.pop()
        self.put_entities_in_xdata(xdata)  

Each subclass puts its own list on top, variable data has to be appended at 
the end and has to be checked by isinstance().
  
class Layer(DXFEntity):
    def dump_resources(self, package: ResourcePackage):
        super().dump_resources(package)
        linetype = self.doc.linetypes.get(self.dxf.linetype)
        package.push([linetype])

    def load_resources(self, package: ResourcePackage):
        linetype, *_ = package.pop()
        self.dxf.name = linetype.dxf.name
        super().load_resources(package)

"""


@runtime_checkable
class RTP(Protocol):
    """ResourceTransferProtocol"""

    def dump_resources(self, package: ResourcePackage) -> None:
        ...

    def load_resources(self, package: ResourcePackage) -> None:
        ...


class ResourcePackageImpl(ResourcePackage):
    def __init__(self, entity: "DXFEntity"):
        self.entity = entity
        self._resources: List[List["DXFEntity"]] = list()

    def push(self, resources: List["DXFEntity"]):
        self._resources.append(resources)

    def pop(self) -> List["DXFEntity"]:
        return self._resources.pop()

    def resources(self) -> Iterator["DXFEntity"]:
        for data in self._resources:
            yield from data

    def foreach(self, func: Callable[["DXFEntity"], "DXFEntity"]):
        self._resources = [
            [func(entity) for entity in entities]
            for entities in self._resources
        ]


class ResourceTransferManager:
    def __init__(self):
        self.packages: Dict[int, ResourcePackageImpl] = dict()

    def register(self, entity: "DXFEntity"):
        if id(entity) not in self.packages:
            package = ResourcePackageImpl(entity)
            assert isinstance(entity, RTP)
            entity.dump_resources(package)
            self.packages[id(entity)] = package

    def transfer(self, target: "Drawing"):
        cloner = EntityCloner()

        # clone resources
        for pkg in self.packages.values():
            cloner.add(pkg.resources())
        cloner.run()
        cloner.bind(target)

        # replace resources by clones
        for pkg in self.packages.values():
            pkg.foreach(cloner.swap)

        assign_resources(cloner.clones.values(), target)

        # update entity resources
        for pkg in self.packages.values():
            rtp = cast("RTP", pkg.entity)
            rtp.load_resources(pkg)


class EntityCloner:
    def __init__(self):
        self.clones: Dict[int, "DXFEntity"] = dict()
        self.originals: Dict[int, "DXFEntity"] = dict()

    def add(self, entities: Iterable["DXFEntity"]):
        for e in entities:
            if id(e) not in self.clones:
                self.originals[id(e)] = e

    def run(self):
        trash = list()
        extend = list()
        while self.originals:
            # do not add/delete while iterating
            trash.clear()
            extend.clear()
            for entity in self.originals.values():
                pkg = ResourcePackageImpl(entity)
                entity.dump_resources(pkg)  # type: ignore
                resources = list(pkg.resources())
                if all(id(e) in self.clones for e in resources):
                    # all resources are cloned
                    trash.append(self._clone(entity))
                else:
                    # add required resources for cloning
                    extend.extend(resources)
            count = len(self.originals)
            stuck = True
            self.add(extend)
            if len(self.originals) != count:
                stuck = False
            for _id in trash:
                if _id:
                    del self.originals[_id]

            # todo: break possible cyclic references!
            if stuck and len(self.originals) == count:
                break

    def _clone(self, entity: "DXFEntity") -> int:
        if id(entity) in self.clones:
            return 0
        self.clones[id(entity)] = entity.copy()
        return id(entity)

    def swap(self, entity: "DXFEntity") -> "DXFEntity":
        return self.clones[id(entity)]

    def bind(self, doc: "Drawing"):
        from ezdxf.entities import factory

        for clone in self.clones.values():
            factory.bind(clone, doc)


def assign_resources(entities: Iterable["DXFEntity"], doc: "Drawing"):
    # TODO: Resources have to be added to the correct resource tables
    pass
