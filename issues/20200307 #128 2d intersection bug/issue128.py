import ezdxf
from ezdxf.math import ConstructionLine


class ConstructionLineExt(ConstructionLine):
    def __init__(self, start: "Vertex", end: "Vertex"):
        super().__init__(start, end)

    def set_all_intersections(self, all_entities, msp):
        intersection_list = []
        for entity in msp.query("*[layer=='laser']i"):
            if entity.dxftype() == "LINE":
                check_line = ConstructionLineExt(entity.dxf.start, entity.dxf.end)

                intersection_point = self.intersect(check_line)
                if intersection_point is not None:
                    msp.add_circle(intersection_point, 0.5, dxfattribs={'layer':'intersection'})
                    intersection_list.append(intersection_point)


dwg = ezdxf.readfile("input_clean.dxf")
msp = dwg.modelspace()

# get all entities
all_org_entities = msp.query("LINE CIRCLE ARC")
test_line = ConstructionLineExt((-10.123123, 30.1234553), (300.2344, 30.1234553))
msp.add_line(test_line.start, test_line.end)
test_line.set_all_intersections(all_org_entities, msp)

dwg.saveas("output_clean.dxf")


dwg = ezdxf.readfile("input_modified.dxf")
msp = dwg.modelspace()

# get all entities
all_org_entities = msp.query("LINE CIRCLE ARC")
test_line = ConstructionLineExt((-10.123123, 30.1234553), (300.2344, 30.1234553))
msp.add_line(test_line.start, test_line.end)
test_line.set_all_intersections(all_org_entities, msp)

dwg.saveas("output_modified.dxf")