# Makefile for Tests
#

test_python_3:
	python3 -m unittest discover -s tests

test_python_2:
	python2 -m unittest discover -s tests

test_pypy:
	python2 -m unittest discover -s tests

tests: test_python_3 test_python_2 test_pypy