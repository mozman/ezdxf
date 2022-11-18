#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""
This the interface module for the resource management module for transferring
DXF resources between documents.

Planning state!!!

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from ezdxf.entities import DXFEntity

__all__ = ["ResourcePackage", "RTP"]


@runtime_checkable
class ResourcePackage(Protocol):
    """A DXFEntity stores all required resources which are stored in the owner
    document as real Python references in the resource Package (not layer or
    linetype names ...).

    The TransferManager creates the required resources in the target document
    and replaces the stored Python object by the new created object and calls
    DXFEntity.load_resources(...), so the entity can update its reference or
    remove resources which can not be transferred.

    """

    def push(self, resources: list[DXFEntity]):
        ...

    def pop(self) -> list[DXFEntity]:
        ...


@runtime_checkable
class RTP(Protocol):
    """ResourceTransferProtocol"""

    def dump_resources(self, package: ResourcePackage) -> None:
        ...

    def load_resources(self, package: ResourcePackage) -> None:
        ...
