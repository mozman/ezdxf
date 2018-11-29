#!/usr/bin/env python3
# Created: 10.03.2011
# Copyright (c) 2011-2018 Manfred Moitzi
# License: MIT License
import os
from setuptools import setup, find_packages
# setuptools docs: https://setuptools.readthedocs.io/en/latest/setuptools.html
VERSION = "0.9a1"  # also update VERSION in __init__.py


def read(fname, until=""):
    def read_until(lines):
        last_index = -1
        for index, line in enumerate(lines):
            if line.startswith(until):
                last_index = index
                break
        return "".join(lines[:last_index])
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as f:
            return read_until(f.readlines()) if until else f.read()
    except IOError:
        return "File '%s' not found.\n" % fname


setup(
    name='ezdxf',
    version=VERSION,
    description='A Python package to create/manipulate DXF drawings.',
    author='Manfred Moitzi',
    url='https://ezdxf.mozman.at',
    download_url='https://pypi.org/project/ezdxf/',
    author_email='me@mozman.at',
    python_requires='>=3.5',
    packages=find_packages(),
    package_data={'ezdxf': ['templates/*.dxf', 'pp/*.html', 'pp/*.js', 'pp/*.css', ]},
    entry_points={
        'console_scripts': [
            'dxfpp = ezdxf.pp.__main__:main',  # DXF Pretty Printer
            'dxfaudit = ezdxf.audit.__main__:main',  # DXF Audit
        ]
    },
    provides=['ezdxf'],
    tests_require=['pytest'],
    install_requires=['pyparsing>=2.0.1'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.rst')+read('NEWS.rst', until='Version 0.7.9'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
