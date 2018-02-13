#!/usr/bin/env python
# Author:  mozman
# Purpose: setup
# Created: 10.03.2011
# License: MIT License


import os
from setuptools import setup

VERSION = "0.8.6"  # also update VERSION in __init__.py
AUTHOR_NAME = 'Manfred Moitzi'
AUTHOR_EMAIL = 'me@mozman.at'


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
    author=AUTHOR_NAME,
    url='https://ezdxf.mozman.at',
    download_url='https://pypi.python.org/pypi/ezdxf/',
    author_email=AUTHOR_EMAIL,
    packages=['ezdxf',
              'ezdxf.legacy',
              'ezdxf.modern',
              'ezdxf.lldxf',
              'ezdxf.pp',
              'ezdxf.sections',
              'ezdxf.templates',
              'ezdxf.tools',
              'ezdxf.addons',
              ],
    package_data={'ezdxf': ['templates/*.dxf',
                            'pp/dxfpp.html',
                            'pp/dxfpp.js',
                            'pp/dxfpp.css',
                            'pp/rawpp.css',
                            'pp/rawpp.html',
                            ]},
    entry_points={
        'console_scripts': [
            'dxfpp = ezdxf.pp.__main__:main',  # DXF Pretty Printer
            'dxfaudit = ezdxf.audit.__main__:main',  # DXF Audit
        ]
    },
    provides=['ezdxf'],
    tests_requires=['pytest'],
    install_requires=['pyparsing>=2.0.1'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.rst')+read('NEWS.rst', until='Version 0.6.5'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
