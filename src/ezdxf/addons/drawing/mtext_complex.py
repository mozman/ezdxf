#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from ezdxf.entities import MText
from .backend import Backend
from .properties import Properties

__all__ = ["complex_mtext_renderer"]


def complex_mtext_renderer(
    backend: Backend, mtext: MText, properties: Properties
) -> None:
    pass
