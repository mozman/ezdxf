# License: MIT-License

BUILD_OPTIONS = setup.py build_ext --inplace --force

PYTHON39 = py -3.9
PYTHON38 = py -3.8
PYTHON37 = py -3.7

cython:
	$(PYTHON38) $(BUILD_OPTIONS)
	$(PYTHON39) $(BUILD_OPTIONS)


packages:
	$(PYTHON37) setup.py bdist_wheel
	$(PYTHON38) setup.py bdist_wheel
	$(PYTHON39) setup.py bdist_wheel
	$(PYTHON38) setup.py sdist --formats=zip
