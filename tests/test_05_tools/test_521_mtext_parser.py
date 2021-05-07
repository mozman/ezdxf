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


class TestMTextContentParsing:
    def test_parse_plain_text(self):
        tokens = list(MTextParser("word1 word2 word3"))
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
        tokens = list(MTextParser(r"\\\{\} \\\{\}"))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.SPACE, TokenType.WORD)
        assert token_data(tokens) == (r"\{}", None, r"\{}")

    def test_single_new_paragraph_token(self):
        tokens = list(MTextParser(r"\P"))
        assert token_types(tokens) == (TokenType.NEW_PARAGRAPH,)

    def test_new_paragraph_token_in_usual_context(self):
        tokens = list(MTextParser(r"word\Pword"))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.NEW_PARAGRAPH, TokenType.WORD
        )

    def test_single_new_column_token(self):
        tokens = list(MTextParser(r"\N"))
        assert token_types(tokens) == (TokenType.NEW_COLUMN,)

    def test_new_column_token_in_usual_context(self):
        tokens = list(MTextParser(r"word\Nword"))
        assert token_types(tokens) == (
            TokenType.WORD, TokenType.NEW_COLUMN, TokenType.WORD
        )

    def test_grouping_level_one(self):
        tokens = list(MTextParser("{word}"))
        assert token_types(tokens) == (
            TokenType.GROUP_START, TokenType.WORD, TokenType.GROUP_END
        )

    def test_grouping_level_two(self):
        tokens = list(MTextParser("{word{word}}"))
        assert token_types(tokens) == (
            TokenType.GROUP_START, TokenType.WORD,
            TokenType.GROUP_START, TokenType.WORD,
            TokenType.GROUP_END,
            TokenType.GROUP_END
        )

    def test_parser_does_not_check_valid_grouping(self):
        tokens = list(MTextParser("{{{}"))
        assert token_types(tokens) == (
            TokenType.GROUP_START,
            TokenType.GROUP_START,
            TokenType.GROUP_START,
            TokenType.GROUP_END
        )


class TestMTextContextParsing:
    def test_switch_underline_on(self):
        tokens = list(MTextParser(r"\Lword"))
        assert len(tokens) == 1, "property changes should not yield tokens"
        ctx, token, data = tokens[0]
        assert ctx.underline is True

    def test_consecutive_tokens_get_the_same_context_objects_if_unchanged(self):
        tokens = list(MTextParser(r"\Lword word"))
        assert len(tokens) == 3
        ctx0, token, data = tokens[0]
        ctx1, token, data = tokens[1]
        ctx2, token, data = tokens[2]
        assert ctx0 is ctx1 and ctx0 == ctx1
        assert ctx1 is ctx2 and ctx1 == ctx2
        # This is the reason why context objects are treated as immutable:
        # If the context doesn't change the tokens can share the same object.

    def test_switch_underline_on_off_creates_different_context_objects(self):
        tokens = list(MTextParser(r"\Lword\lword"))
        assert len(tokens) == 2
        ctx0, token, data = tokens[0]
        ctx1, token, data = tokens[1]
        assert ctx0.underline is not ctx1.underline
        assert ctx0 != ctx1

    def test_switch_overline_on_off(self):
        mp = MTextParser(r"\Oword\o")
        tokens = list(mp)
        assert len(tokens) == 1
        ctx, token, data = tokens[0]
        # attribute context store the final context
        final_ctx = mp.ctx
        assert ctx.overline is not final_ctx.overline
        assert ctx != final_ctx

    def test_switch_strike_through_on_off(self):
        mp = MTextParser(r"\Kword word\k")
        tokens = list(mp)
        assert len(tokens) == 3
        ctx, token, data = tokens[2]
        final_ctx = mp.ctx
        assert ctx.strike_through is not final_ctx.strike_through
        assert ctx != final_ctx


if __name__ == '__main__':
    pytest.main([__file__])
