# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.readfile(r'C:\Users\manfred\Desktop\now\ACAD_R2004.dxf')
msp = doc.modelspace()

OLD_LAYER_NAME = 'TITEL_025'
NEW_LAYER_NAME = 'MOZMAN'

# rename layer
try:
    layer = doc.layers.get(OLD_LAYER_NAME)
except ValueError:
    print(f'Layer {OLD_LAYER_NAME} not found.')
else:
    layer.dxf.name = NEW_LAYER_NAME

# move entities in model space to new layer
all_entities_on_old_layer = doc.modelspace().query(f'*[layer=="{OLD_LAYER_NAME}"]')
for entity in all_entities_on_old_layer:
    entity.dxf.layer = NEW_LAYER_NAME

doc.saveas(r'C:\Users\manfred\Desktop\now\renamed_layer.dxf')
