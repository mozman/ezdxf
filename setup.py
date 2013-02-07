#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: setup
# Created: 10.03.2011
#
#    Copyright (C) 2011  Manfred Moitzi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from distutils.core import setup

from ezdxf import VERSION

AUTHOR_NAME = 'Manfred Moitzi'
AUTHOR_EMAIL = 'mozman@gmx.at'

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return "File '%s' not found.\n" % fname

setup(name='ezdxf',
    version=VERSION,
    description='A Python package to create/manipulate DXF drawings.',
    author=AUTHOR_NAME,
    url='http://bitbucket.org/mozman/ezdxf',
    download_url='http://bitbucket.org/mozman/ezdxf/downloads',
    author_email=AUTHOR_EMAIL,
    packages=['ezdxf', 'ezdxf.ac1009', 'ezdxf.ac1015', 'ezdxf.ac1018', 'ezdxf.ac1021', 'ezdxf.ac1024'],
    package_data={'ezdxf': ['templates/*.dxf']},
    provides=['ezdxf'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.txt')+read('NEWS.txt'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]
     )
