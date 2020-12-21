from pathlib import Path
import logging
import ezdxf
from ezdxf.proxygraphic import ProxyGraphicDebugger

ezdxf.options.load_proxy_graphics = True

OUTBOX = Path('~/Desktop/Outbox').expanduser()
logging.basicConfig(filename=OUTBOX / "ezdxf-log.txt", level='DEBUG')
logger = logging.getLogger('ezdxf')

EXAMPLE = Path(ezdxf.EZDXF_TEST_FILES) / "mleader" / "mbway-mleader.dxf"

doc = ezdxf.readfile(EXAMPLE)
mleader = doc.entitydb['403']
with open(OUTBOX / "proxy-debug.txt", mode="wt") as stream:
    proxy = ProxyGraphicDebugger(mleader.proxy_graphic, doc,
                                 debug_stream=stream)
    proxy.log_commands()
    proxy.log_entities()

logging.shutdown()
