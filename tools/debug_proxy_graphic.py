#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import logging
import ezdxf
from ezdxf.proxygraphic import ProxyGraphicDebugger

ezdxf.options.load_proxy_graphics = True

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

logging.basicConfig(filename=CWD / "ezdxf-log.txt", level="DEBUG")
logger = logging.getLogger("ezdxf")

EXAMPLE = ezdxf.options.test_files_path / "mleader" / "mbway-mleader.dxf"

doc = ezdxf.readfile(EXAMPLE)
mleader = doc.entitydb["403"]
with open(CWD / "proxy-debug.txt", mode="wt") as stream:
    proxy = ProxyGraphicDebugger(
        mleader.proxy_graphic, doc, debug_stream=stream
    )
    proxy.log_commands()
    proxy.log_entities()

logging.shutdown()
