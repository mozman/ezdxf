import ezdxf

drawing = ezdxf.readfile("/home/harrison/0138_F.dxf")
modelspace = drawing.modelspace()

select_handles = set([])
delete_handles = set([])

queries = [
    'INSERT[layer=="h-rack"]i',
    'INSERT[layer=="h-laydown_area_p"]i',
    'CIRCLE[layer=="h-text"]i',
]

for q in queries:
    result = modelspace.query(q)

    for e in result:
        select_handles.add(e.dxf.handle)

for e in drawing.entities:
    if e.dxf.handle not in select_handles:
        delete_handles.add(e.dxf.handle)

for h in delete_handles:
    e = drawing.get_dxf_entity(h)
    if modelspace.__contains__(e):
        modelspace.delete_entity(e)

drawing.saveas("/tmp/testing.dxf")