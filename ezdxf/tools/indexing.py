# created: 23.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License


class Index(object):
    def __init__(self, item):
        try:
            self.length = len(item)
        except TypeError:
            self.length = int(item)

    def index(self, item):
        if item < 0:
            return self.length + int(item)
        else:
            return int(item)

    def slicing(self, *args):
        if isinstance(args[0], slice):
            s = args[0]
        else:
            s = slice(*args)
        start, end, stride = s.indices(self.length)
        if start < end:
            if stride < 0:
                return
            while start < end:
                yield start
                start += stride
        else:
            if stride > 0:
                return
            while start > end:
                yield start
                start += stride
