#!/usr/bin/env python
# Author:  mozman
# Purpose: setup
# Created: 10.03.2011
# License: MIT License

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
    packages=['ezdxf', 'ezdxf.ac1009', 'ezdxf.ac1015', 'ezdxf.ac1018', 'ezdxf.ac1021', 'ezdxf.ac1024', 'ezdxf.ac1027'],
    package_data={'ezdxf': ['templates/*.dxf']},
    provides=['ezdxf'],
    keywords=['DXF', 'CAD'],
    long_description=read('README.rst')+read('NEWS.rst'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]
     )
