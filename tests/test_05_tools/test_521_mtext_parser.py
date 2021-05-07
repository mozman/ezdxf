#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextContext, MTextParser, TokenType, TextScanner


class TestTextScanner:
    def test_scan_empty_text(self):
        s = TextScanner("")
        assert s.is_empty is True
        assert s.peek() == ""  # empty string signals end of text
        assert s.get() == ""
        s.undo()
        assert s.is_empty is True, "should be still empty"

    def test_non_empty_string_is_not_empty(self):
        s = TextScanner("word")
        assert s.is_empty is False

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

    def test_getting_all_letters_empties_scanner(self):
        s = TextScanner("w")
        s.get()
        assert s.is_empty is True

    def test_undo_one_letter(self):
        s = TextScanner("w")
        s.get()
        s.undo()
        assert s.is_empty is False
        assert s.peek() == "w"


def token_types(tokens):
    return tuple(token for ctx, token, data in tokens)


def token_data(tokens):
    return tuple(data for ctx, token, data in tokens)


class TestMTextParser:
    def test_parse_plain_text(self):
        content = "word1 word2 word3"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.SPACE, TokenType.WORD, TokenType.SPACE,
            TokenType.WORD
        )
        assert token_data(tokens) == ("word1", None, "word2", None, "word3")

    def test_three_adjacent_spaces(self):
        tokens = list(MTextParser("   "))
        assert token_types(tokens) == (
            TokenType.SPACE, TokenType.SPACE, TokenType.SPACE)

    def test_non_breaking_space(self):
        tokens = list(MTextParser(r"word\~word"))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.NBSP, TokenType.WORD)

    def test_space_and_adjacent_non_breaking_space(self):
        tokens = list(MTextParser(r"word \~ word"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.SPACE, TokenType.NBSP, TokenType.SPACE,
            TokenType.WORD
        )

    def test_escaped_letters_building_words(self):
        content = r"\\\{\} \\\{\}"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.SPACE, TokenType.WORD)
        assert token_data(tokens) == (r"\{}", None, r"\{}")

    def test_single_new_paragraph_token(self):
        content = r"\P"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (TokenType.NEW_PARAGRAPH,)

    def test_new_paragraph_token_in_usual_context(self):
        content = r"word\Pword"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.NEW_PARAGRAPH, TokenType.WORD
        )

    def test_single_new_column_token(self):
        content = r"\N"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (TokenType.NEW_COLUMN,)

    def test_new_column_token_in_usual_context(self):
        content = r"word\Nword"
        tokens = list(MTextParser(content))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.NEW_COLUMN, TokenType.WORD
        )


if __name__ == '__main__':
    pytest.main([__file__])
