# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

BUILD_OPTIONS = setup.py build_ext --inplace --force
ACC = src/ezdxf/acc

PYTHON39 = py -3.9
PYTHON38 = py -3.8
PYTHON37 = py -3.7
PYPY3 = pypy3

.PHONY: build

build:
	$(PYTHON39) $(BUILD_OPTIONS)

test0: build
	$(PYTHON39) -m pytest tests

test1: test0
	$(PYTHON39) -m pytest integration_tests

all:
	$(PYTHON37) $(BUILD_OPTIONS)
	$(PYTHON38) $(BUILD_OPTIONS)
	$(PYTHON39) $(BUILD_OPTIONS)

clean:
	rm -f $(ACC)/*.pyd
	rm -f $(ACC)/*.html
	rm -f $(ACC)/fastmath.c

packages:
	$(PYTHON37) setup.py bdist_wheel
	$(PYTHON38) setup.py bdist_wheel
	$(PYTHON39) setup.py bdist_wheel
	$(PYTHON38) setup.py sdist --formats=zip
