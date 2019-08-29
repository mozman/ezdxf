import ezdxf

FILENAME = "JR-3099-V2-LTCSL-4X-S.dxf"
NEW_FILENAME = "JR-3099-V2-LTCSL-4X-S-repair.dxf"


class GerberFileError(Exception):
    pass


def repair_gerber_file(filename, new_file_name):
    def get_first_section_index():
        i = 2
        while lines[i] != '  0\n' and lines[i + 1] != 'SECTION\n':
            i += 2
        return i

    with open(filename, mode='rt') as f:
        lines = f.readlines()
    if lines[0] == '999\n' and lines[1] == 'Version 1.0, Gerber Technology.\n':
        index = get_first_section_index()
        with open(new_file_name, mode='wt', encoding='cp1252') as f:
            f.writelines(lines[index:])
    else:
        raise GerberFileError('"{}" is not a Gerber file.'.format(filename))


try:
    repair_gerber_file(FILENAME, NEW_FILENAME)
    doc = ezdxf.readfile(NEW_FILENAME)
except GerberFileError:  # it is NOT a Gerber file
    doc = ezdxf.readfile(FILENAME)

print('File "{}" contains {} entities in the modelspace.'.format(doc.filename, len(doc.modelspace())))
