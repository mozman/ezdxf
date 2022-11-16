#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

"""
Resource management module for transferring DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import Iterator, cast, Callable, Iterable
from ezdxf.respkg import RTP
from ezdxf.entities import DXFEntity, factory
from ezdxf.document import Drawing

# The goal is that this module should not be imported from any module which
# implements DXF entities, so that this module can import necessary resource
# entities like Layer, Linetype or MLeaderStyle

__all__ = ["ResourceTransferManager"]

"""
Extension dictionaries: handled in DXFEntity.copy() and factory.bind()

Reactors? 
I think reactors in resources can be dropped. 
Under no circumstances should reactors initiate a copy process of the 
referenced entities.

Block references? 
The BLOCK_RECORD is a table entry and somehow a resource. 
But the BLOCK_RECORD also represents paperspace layouts, block layouts, the
modelspace and whole documents as XREFs.

Handles in the XDATA section? 
Handle references in XDATA in order of appearance:

class DXFEntity:
    def dump_resources(self, package: ResourcePackage):
        package.push(self.get_entities_in_xdata())

    def get_entities_in_xdata(self):
        # in order of appearance
        e1 = 1. 1005 -> 1. get entity by handle
        e2 = 2. 1003 -> 2. get layer entity by name
        e3 = 3. 1005 -> 3. get entity by handle
        return [e1, e2, e3]
    
    def put_entities_in_xdata(self, entities):
        for e in entities:
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


class _ResourcePackage:
    def __init__(self, entity: DXFEntity):
        self.entity = entity
        self._resources: list[list[DXFEntity]] = list()

    def push(self, resources: list[DXFEntity]):
        self._resources.append(resources)

    def pop(self) -> list[DXFEntity]:
        return self._resources.pop()

    def resources(self) -> Iterator[DXFEntity]:
        for data in self._resources:
            yield from data

    def foreach(self, func: Callable[[DXFEntity], DXFEntity]):
        self._resources = [
            [func(entity) for entity in entities]
            for entities in self._resources
        ]


class ResourceTransferManager:
    def __init__(self) -> None:
        self.packages: dict[int, _ResourcePackage] = dict()
        self.copy_machine = CopyMachine()

    def register(self, entity: DXFEntity):
        """Register resources."""
        if id(entity) not in self.packages:
            package = _ResourcePackage(entity)
            assert isinstance(entity, RTP)
            entity.dump_resources(package)
            self.packages[id(entity)] = package

    def transfer(self, target: Drawing):
        """Transfer resources if the transaction can be finished completely.
        """
        self.copy_all()
        if self.copy_machine.has_finished():
            # TODO: order of execution?
            self.swap_resources()
            self.update_entities()
            bind(self.copy_machine.copies, target)
            assign_resources(self.copy_machine.copies, target)

    def copy_all(self):
        """Copy resources."""
        for pkg in self.packages.values():
            # Important: copy only the resources, the entity copy itself is
            # another task!
            self.copy_machine.append(pkg.resources())
        self.copy_machine.run()

    def swap_resources(self):
        """Replace resources by copies."""
        for pkg in self.packages.values():
            pkg.foreach(self.copy_machine.swap)

    def update_entities(self):
        """Update entity resources."""
        for pkg in self.packages.values():
            rtp = cast("RTP", pkg.entity)
            rtp.load_resources(pkg)


class CopyMachine:
    def __init__(self) -> None:
        self._copies: dict[int, DXFEntity] = dict()
        self._originals: dict[int, DXFEntity] = dict()

    @property
    def copies(self) -> Iterable[DXFEntity]:
        """Returns the copies"""
        return self._copies.values()

    def has_finished(self) -> bool:
        """All resources are copied?"""
        return not len(self._originals)

    def append(self, entities: Iterable[DXFEntity]):
        """Append entities to copy."""
        for e in entities:
            if id(e) not in self._copies:
                self._originals[id(e)] = e

    def run(self):
        """Execute copy process."""
        trash = list()
        new = list()
        while self._originals:
            # do not add/delete while iterating
            trash.clear()
            new.clear()
            for entity in self._originals.values():
                pkg = _ResourcePackage(entity)
                entity.dump_resources(pkg)  # type: ignore
                resources = list(pkg.resources())
                if all(id(e) in self._copies for e in resources):
                    # all resources are copied
                    trash.append(self.copy_entity(entity))
                else:
                    # add required resources to copy
                    new.extend(resources)
            count = len(self._originals)
            stuck = True
            self.append(new)
            if len(self._originals) != count:
                stuck = False
            for _id in trash:
                if _id:
                    del self._originals[_id]
            if stuck and len(self._originals) == count:
                break

    def copy_entity(self, entity: DXFEntity) -> int:
        """Copy a single entity and returns the id or 0 if the entity is
        already copied.
        """
        if id(entity) in self._copies:
            return 0
        self._copies[id(entity)] = entity.copy()
        return id(entity)

    def swap(self, entity: DXFEntity) -> DXFEntity:
        """Swap original entity against copy."""
        return self._copies[id(entity)]


def bind(entities: Iterable[DXFEntity], doc: Drawing):
    """Bind all entities to the DXF document."""
    for entity in entities:
        factory.bind(entity, doc)


def assign_resources(entities: Iterable[DXFEntity], doc: Drawing):
    """Add entities to the correct resource tables."""
    pass
