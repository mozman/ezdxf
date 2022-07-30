#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from setuptools import Extension, setup

setup(
    name="tricy",
    ext_modules=[
        Extension(
            "tricy",
            ["tricy.pyx"],
            language="c++",
            include_dirs=[
                r"..\src\ezdxf\acc",
            ],
        ),
    ],
)

# build c-extensions in archive:
# py(thon3) setup.py build_ext -i
