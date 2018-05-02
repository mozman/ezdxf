# created: 23.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License


class Index(object):
    def __init__(self, item):
        try:
            self.length = len(item)
        except TypeError:
            self.length = int(item)

    def index(self, item, error=None):
        if item < 0:
            result = self.length + int(item)
        else:
            result = int(item)
        if error and not (0 <= result < self.length):
            raise error('index out of range')
        return result

    def slicing(self, *args):
        if isinstance(args[0], slice):
            s = args[0]
        else:
            s = slice(*args)
        return range(*s.indices(self.length))
