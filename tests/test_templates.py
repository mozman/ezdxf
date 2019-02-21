# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import os
import unittest

from ezdxf.templates import TemplateLoader


class TestTemplateLoader(unittest.TestCase):
    def test_filename(self):
        finder = TemplateLoader()
        self.assertEqual('ABC.dxf', finder.filename('ABC'))

    def test_filepath(self):
        finder = TemplateLoader()
        result = finder.filepath('AC1009')
        filename = os.path.join('ezdxf', 'templates', 'AC1009.dxf')
        self.assertTrue(result.endswith(filename))

    def test_set_templatepath(self):
        finder = TemplateLoader('templates')
        result = finder.filepath('AC1009')
        self.assertEqual(os.path.join('templates', 'AC1009.dxf'), result)

    def test_set_templatedir(self):
        finder = TemplateLoader('templates')
        finder.templatedir = 'templates2'
        self.assertEqual('templates2', finder.templatedir)


if __name__ == '__main__':
    unittest.main()