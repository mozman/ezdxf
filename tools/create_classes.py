from pathlib import Path
import ezdxf

FILENAME = Path('xxx.dxf')

doc = ezdxf.readfile(FILENAME) if FILENAME.exists() else ezdxf.new('R2018')

FMT = """    '{name}': ['{cpp}', '{app}', {flags}, {proxy}, {entity}],\n"""
with open('class_definitions.txt', mode='wt') as f:
    f.write('CLASSES = {\n')
    for cls in doc.sections.classes:
        f.write(FMT.format(
            name=cls.dxf.name,
            cpp=cls.dxf.cpp_class_name,
            app=cls.dxf.app_name,
            flags=cls.get_dxf_attrib('flags', 0),
            proxy=cls.get_dxf_attrib('was_a_proxy', 0),
            entity=cls.get_dxf_attrib('is_an_entity', 0),
        ))
    f.write('}\n')
