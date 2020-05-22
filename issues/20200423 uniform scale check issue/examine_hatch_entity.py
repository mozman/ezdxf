from pathlib import Path
import ezdxf
import logging
DIR = Path('~/Desktop/Inbox/ezdxf').expanduser()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ezdxf')


doc = ezdxf.readfile(DIR / '417.dxf')

msp = doc.modelspace()

for flag_ref in msp.query('INSERT'):
    print(f'Block reference: {str(flag_ref)}')
    for entity in flag_ref.virtual_entities():
        if entity.dxftype() == 'HATCH':
            print("  HATCH:", entity.dxf.pattern_name)
