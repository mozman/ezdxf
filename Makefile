# Makefile for Tests
#
.PHONY: unittests integration_tests
INTEGRATION_TESTS = $(shell cd integration_tests && find -name "*.py")

test_python_3: PYTHON=python3
test_python_3: unittests integration_tests;

test_python_2: PYTHON=python2
test_python_2: unittests integration_tests;

test_pypy: PYTHON=pypy
test_pypy: unittests integration_tests;


unittests:
	$(PYTHON) -m unittest discover -s tests

integration_tests:
	cd integration_tests ; \
	for test in $(INTEGRATION_TESTS) ; do \
        $(PYTHON) $$test ; \
    done


all:
	$(MAKE) test_python_2
	$(MAKE) test_python_3
	$(MAKE) test_pypy

sdist:
	py setup.py sdist --formats=zip,gztar upload
