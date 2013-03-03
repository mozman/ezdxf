#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test database
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest

from ezdxf.database import EntityDB


class testEntityDB(unittest.TestCase):
    def setUp(self):
        self.db = EntityDB()
        self.db[0] = 'TEST'

    def test_get_value(self):
        self.assertEqual('TEST', self.db[0])

    def test_set_value(self):
        self.db[0] = 'XTEST'
        self.assertEqual('XTEST', self.db[0])

    def test_del_value(self):
        del self.db[0]
        with self.assertRaises(KeyError):
            self.db[0]


if __name__ == '__main__':
    unittest.main()