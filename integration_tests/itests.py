#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: itest.py
# Created: 28.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import os
import glob

if sys.version_info[0] < 3:
    print("Python 3 interpreter is required")
    sys.exit(1)

ezdxfdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

if ezdxfdir not in sys.path:
    print("Adding '%s' to python path." % ezdxfdir)
    sys.path.insert(0, ezdxfdir)

def print_available_tests():
    print("available tests:")
    for filename in glob.glob(os.path.join(os.path.dirname(__file__), '*.py')):
        if not filename.endswith('itests.py'):
            print(os.path.basename(filename))


if __name__=='__main__':
    print_available_tests()
