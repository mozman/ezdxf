#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import MTextParser, TokenType


def token_types(tokens):
    return tuple(token.type for token in tokens)


def token_data(tokens):
    return tuple(token.data for token in tokens)


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

    def test_grouping_chars_do_not_yield_tokens(self):
        tokens = list(MTextParser("{word{word}}"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.WORD,
        )

    def test_parser_does_not_check_valid_grouping(self):
        tokens = list(MTextParser("{{{}"))
        assert len(tokens) == 0

    def test_wrap_at_dimline(self):
        mp = MTextParser(r"1\X2")
        tokens = list(mp)
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.WRAP_AT_DIMLINE,
            TokenType.WORD,
        )

    def test_decode_special_encodings(self):
        token = list(MTextParser("%%c%%d%%p%%C%%D%%P"))[0]
        assert token.data == "Ø°±Ø°±"

    def test_unknown_special_encodings(self):
        # underline codes in TEXT are not supported in MTEXT:
        token = list(MTextParser("%%a%%uTEXT%%u%%z"))[0]
        assert token.data == "%%a%%uTEXT%%u%%z"

    def test_percent_sign_usage(self):
        token = list(MTextParser("%_%%_%%%_%%%%"))[0]
        assert token.data == "%_%%_%%%_%%%%"


class TestParsingFractions:
    def test_simple_horizontal_fraction(self):
        token = list(MTextParser("\\S1/2;"))[0]
        assert token.data == ("1", "2", "/")

    def test_simple_diagonal_fraction(self):
        token = list(MTextParser("\\S1#2;"))[0]
        assert token.data == ("1", "2", "#")

    def test_simple_limit_style_fraction(self):
        token = list(MTextParser("\\S1^ 2;"))[0]
        assert token.data == ("1", "2", "^")

    def test_without_terminator_parsing_until_end_of_string(self):
        token = list(MTextParser("\\S1/2"))[0]
        assert token.data == ("1", "2", "/")

    def test_escape_terminator_char(self):
        token = list(MTextParser("\\S1\\;/2;"))[0]
        assert token.data == ("1;", "2", "/")

    def test_escape_backslash_char(self):
        token = list(MTextParser("\\S\\\\1/\\\\2;"))[0]
        assert token.data == ("\\1", "\\2", "/")

    def test_escape_stacking_type_char(self):
        token = list(MTextParser("\\S1\\/2;"))[0]
        assert token.data == ("1/2", "", "")
        token = list(MTextParser("\\S1\\#2;"))[0]
        assert token.data == ("1#2", "", "")

    def test_escape_caret_char(self):
        token = list(MTextParser("\\S1\\^ 2;"))[0]
        # This is not like AutoCAD/BricsCAD, which render: 1^2 without a space
        # AutoCAD/BricsCAD caret decode the chars before parsing the content.
        # IMHO: escaping the caret should also avoid caret decoding of the
        # following space " "
        assert token.data == ("1^ 2", "", "")
        token = list(MTextParser("\\S\\^J^ 2;"))[0]
        assert token.data == ("^J", "2", "^")

    def test_remove_backslash_escape_char(self):
        token = list(MTextParser("\\S\\N^ \\P;"))[0]
        assert token.data == ("N", "P", "^")

    def test_parse_only_the_first_stacking_type_char(self):
        token = list(MTextParser("\\S1/2/3;"))[0]
        assert token.data == ("1", "2/3", "/")
        token = list(MTextParser("\\S1#2/3;"))[0]
        assert token.data == ("1", "2/3", "#")

    def test_parse_caret_char(self):
        token = list(MTextParser("\\S1^ 2^ 3;"))[0]
        assert token.data == ("1", "2^3", "^")

    def test_without_stacking_type_char(self):
        token = list(MTextParser("\\S123;"))[0]
        assert token.data == ("123", "", "")


class TestMTextContextParsing:
    def test_switch_underline_on(self):
        tokens = list(MTextParser(r"\Lword"))
        assert len(tokens) == 1, "property changes should not yield tokens"
        assert tokens[0].ctx.underline is True

    def test_consecutive_tokens_get_the_same_context_objects_if_unchanged(self):
        tokens = list(MTextParser(r"\Lword word"))
        t0, t1, t2 = tokens
        assert t0.ctx is t1.ctx and t0.ctx == t1.ctx
        assert t1.ctx is t2.ctx and t1.ctx == t2.ctx
        # This is the reason why context objects are treated as immutable:
        # If the context doesn't change the tokens can share the same object.

    def test_switch_underline_on_off_creates_different_context_objects(self):
        tokens = list(MTextParser(r"\Lword\lword"))
        t0, t1 = tokens
        assert t0.ctx.underline is not t1.ctx.underline
        assert t0.ctx != t1.ctx

    def test_switch_overline_on_off(self):
        mp = MTextParser(r"\Oword\o")
        tokens = list(mp)
        assert len(tokens) == 1
        t0 = tokens[0]
        # attribute context store the final context
        final_ctx = mp.ctx
        assert t0.ctx.overline is not final_ctx.overline
        assert t0.ctx != final_ctx

    def test_switch_strike_through_on_off(self):
        mp = MTextParser(r"\Kword word\k")
        tokens = list(mp)
        t0, t1, t2 = tokens
        final_ctx = mp.ctx
        assert t2.ctx.strike_through is not final_ctx.strike_through
        assert t2.ctx != final_ctx

    def test_context_stack_for_grouping(self):
        t0, t1, t2 = MTextParser(r"word{\Lword}word")
        assert t0.ctx.underline is False
        assert t1.ctx.underline is True
        assert t2.ctx.underline is False
        assert t0.ctx is not t1.ctx
        assert t0.ctx is t2.ctx, "initial context should be restored"

    def test_bottom_alignment_with_terminator(self):
        tokens = list(MTextParser(r"\A0;word"))
        assert len(tokens) == 1
        t0 = tokens[0]
        assert t0.data == "word", "terminator should be removed"
        assert t0.ctx.align == 0

    def test_middle_alignment_without_terminator(self):
        tokens = list(MTextParser(r"\A10"))
        assert len(tokens) == 1
        assert tokens[0].ctx.align == 1

    def test_top_alignment_without_terminator(self):
        tokens = list(MTextParser(r"\A2word"))
        assert len(tokens) == 1
        assert tokens[0].ctx.align == 2

    def test_alignment_default_value_for_invalid_argument(self):
        tokens = list(MTextParser(r"\A3word"))
        assert len(tokens) == 1
        t0 = tokens[0]
        assert t0.ctx.align == 0
        assert t0.data == "word", "invalid argument should be removed"


if __name__ == '__main__':
    pytest.main([__file__])
