import ezdxf

drawing = ezdxf.readfile("test.dxf")
modelspace = drawing.modelspace()


all_entities_to_delete = modelspace.query('*')  # start with all entities from model space
all_entities_to_delete.remove('INSERT[layer=="h-rack" | layer=="h-laydown_area_p"]i')  # combines 2 queries with OR
all_entities_to_delete.remove('CIRCLE[layer=="h-text"]i')

for e in all_entities_to_delete:  # contains only entities from model space
    modelspace.delete_entity(e)

drawing.saveas("test_purged.dxf")
