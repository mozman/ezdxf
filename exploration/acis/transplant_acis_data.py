import ezdxf

DONOR = "torus_r2010.dxf"
RECIPIENT = "torus_r2000.dxf"

donor_doc = ezdxf.readfile(DONOR)
donor = donor_doc.modelspace()[0]

recipient_doc = ezdxf.readfile(RECIPIENT)
recipient = recipient_doc.modelspace()[0]


# Implant donor ACIS entity into recipient entity
recipient.sat = donor.sat
patient_name = f"patient_{recipient_doc.acad_release}.dxf"
recipient_doc.saveas(patient_name)


# reload
patient = ezdxf.readfile(patient_name)
entity = patient.modelspace()[0]

with open("implant.sat", "wt") as fp:
    fp.write("\n".join(entity.acis_data))
