#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import TextScanner


class TestTextScanner:
    def test_scan_empty_text(self):
        s = TextScanner("")
        assert s.is_empty is True
        assert s.has_data is False
        assert s.peek() == ""  # empty string signals end of text
        assert s.get() == ""

    def test_non_empty_string_is_not_empty(self):
        s = TextScanner("word")
        assert s.is_empty is False
        assert s.has_data is True

    def test_peeking_next_letter(self):
        s = TextScanner("word")
        assert s.peek() == "w"

    def test_peeking_more_letters_ahead(self):
        s = TextScanner("word")
        assert s.peek(1) == "o"
        assert s.peek(2) == "r"

    def test_peeking_beyond_word_boundaries_returns_empty_string(self):
        s = TextScanner("word")
        assert s.peek(4) == ""

    def test_getting_next_letter_forwards_scan_position(self):
        s = TextScanner("word")
        assert s.get() == "w"
        assert s.peek() == "o"

    def test_consume_one_letter(self):
        s = TextScanner("word")
        s.consume()
        assert s.peek() == "o"

    def test_consume_two_letter(self):
        s = TextScanner("word")
        s.consume(2)
        assert s.peek() == "r"

    def test_getting_all_letters_empties_scanner(self):
        s = TextScanner("w")
        s.get()
        assert s.is_empty is True
        assert s.has_data is False

    def test_can_not_consume_zero_chars(self):
        s = TextScanner("w")
        pytest.raises(ValueError, s.consume, 0)

    def test_can_not_consume_negative_chars(self):
        s = TextScanner("w")
        pytest.raises(ValueError, s.consume, -1)

    def test_can_not_peek_in_reverse_direction(self):
        s = TextScanner("w")
        pytest.raises(ValueError, s.peek, -1)

    def test_find_next_char(self):
        assert TextScanner(";").find(';') == 0
        assert TextScanner("word;").find(';') == 4
        assert TextScanner("word;;").find(';') == 4

    def test_find_ignores_escaped_chars(self):
        assert TextScanner("word\\;;").find(';', escape=True) == 6
        assert TextScanner("word\\n;").find(';', escape=True) == 6
        assert TextScanner("word\\;\\;;").find(';', escape=True) == 8

    def test_find_next_backslash(self):
        assert TextScanner("\\").find('\\') == 0
        assert TextScanner("a\\").find('\\', escape=False) == 1
        assert TextScanner("a\\").find('\\', escape=True) == 1
        assert TextScanner("a\\\\").find('\\', escape=True) == -1
        assert TextScanner("a\\\\\\").find('\\', escape=True) == 3

    def test_not_find_next(self):
        assert TextScanner("").find(';') == -1
        assert TextScanner("word").find(';') == -1
        assert TextScanner("\\;").find(';', escape=True) == -1

    def test_substr_at_the_begin(self):
        assert TextScanner("").substr(0) == ""
        assert TextScanner("a").substr(1) == "a"
        assert TextScanner("ab").substr(1) == "a", \
            "do not return the char at the index itself"
        assert TextScanner("ab").substr(2) == "ab"
        assert TextScanner("ab").substr(3) == "ab"

    def test_substr_from_consumed_string(self):
        s = TextScanner("abcdef")
        s.consume(2)
        assert s.substr(2) == ""
        assert s.substr(3) == "c"
        assert s.substr(4) == "cd"
        assert s.substr(10) == "cdef"

    def test_substr_index_error(self):
        with pytest.raises(IndexError):
            TextScanner("").substr(-1)
        s = TextScanner("abcd")
        s.consume(2)
        with pytest.raises(IndexError):
            s.substr(1)


if __name__ == '__main__':
    pytest.main([__file__])
