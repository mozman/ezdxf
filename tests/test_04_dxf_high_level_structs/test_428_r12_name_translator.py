#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import string
from ezdxf.r12strict import R12NameTranslator


@pytest.fixture
def tr() -> R12NameTranslator:
    return R12NameTranslator()


def test_translate_empty_string(tr):
    assert tr.translate("") == ""
    assert tr.translate("") == ""
    assert len(tr.used_r12_names) == 1
    assert len(tr.translated_names) == 1


def test_translate_uppercase_letters(tr):
    assert tr.translate(string.ascii_uppercase) == string.ascii_uppercase


def test_translate_lowercase_letters(tr):
    assert tr.translate(string.ascii_lowercase) == string.ascii_uppercase


def test_translate_digits(tr):
    assert tr.translate(string.digits) == string.digits


def test_translate_special_chars(tr):
    assert tr.translate("$_-*") == "$_-*"


def test_translate_punctuation(tr):
    """Punctuations are not supported"""
    assert tr.translate(".,;:!?\\/") == "________"


def test_translation_spaces(tr):
    """Spaces are not supported"""
    assert tr.translate("  ") == "__"


def test_translate_invalid_chars_to_underscores(tr):
    assert tr.translate("+abc;") == "_ABC_"


def test_get_same_translations_for_same_names(tr):
    assert tr.translate("+abc;") == "_ABC_"
    assert tr.translate("+abc;") == "_ABC_", "expected the same translation"
    assert len(tr.used_r12_names) == 1
    assert len(tr.translated_names) == 1


def test_unique_names_for_same_r12_translations(tr):
    assert tr.translate("+abc") == "_ABC"
    assert tr.translate("#abc") == "_ABC0"  # basic translation is also _ABC


def test_names_case_insensitive(tr):
    assert tr.translate("Continuous") == "CONTINUOUS"
    assert tr.translate("CONTINUOUS") == "CONTINUOUS"
    assert len(tr.used_r12_names) == 1
    assert len(tr.translated_names) == 1


def test_limit_length_of_long_names(tr):
    name = string.ascii_letters + string.digits
    assert len(tr.translate(name)) == 31


def test_translate_long_names(tr):
    name0 = string.ascii_letters + string.digits
    name1 = name0 + "#"
    assert tr.translate(name0) != tr.translate(name1)
    assert tr.translate(name0) == tr.translate(name0)
    assert tr.translate(name1) == tr.translate(name1)
    assert len(tr.used_r12_names) == 2
    assert len(tr.translated_names) == 2


if __name__ == '__main__':
    pytest.main([__file__])
