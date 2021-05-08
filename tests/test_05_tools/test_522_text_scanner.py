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


if __name__ == '__main__':
    pytest.main([__file__])
