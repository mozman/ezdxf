#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.enums import MTextParagraphAlignment
from ezdxf.tools.text import (
    MTextParser,
    TokenType,
    ParagraphProperties,
)


def token_types(tokens):
    return tuple(token.type for token in tokens)


def token_data(tokens):
    return tuple(token.data for token in tokens)


class TestMTextContentParsing:
    def test_parse_plain_text(self):
        tokens = list(MTextParser("word1 word2 word3"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.SPACE,
            TokenType.WORD,
            TokenType.SPACE,
            TokenType.WORD,
        )
        assert token_data(tokens) == ("word1", None, "word2", None, "word3")

    def test_three_adjacent_spaces(self):
        tokens = list(MTextParser("   "))
        assert token_types(tokens) == (
            TokenType.SPACE,
            TokenType.SPACE,
            TokenType.SPACE,
        )

    def test_non_breaking_space(self):
        tokens = list(MTextParser(r"word\~word"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.NBSP,
            TokenType.WORD,
        )

    def test_space_and_adjacent_non_breaking_space(self):
        tokens = list(MTextParser(r"word \~ word"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.SPACE,
            TokenType.NBSP,
            TokenType.SPACE,
            TokenType.WORD,
        )

    def test_tabulator_caret_I(self):
        tokens = list(MTextParser(r"word^Iword"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.TABULATOR,
            TokenType.WORD,
        )
        assert token_data(tokens) == ("word", None, "word")

    def test_new_paragraph_caret_J(self):
        tokens = list(MTextParser(r"word^Jword"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.NEW_PARAGRAPH,
            TokenType.WORD,
        )
        assert token_data(tokens) == ("word", None, "word")

    def test_replace_caret_chars_by_space(self):
        tokens = list(MTextParser(r"word^Mword"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.SPACE,
            TokenType.WORD,
        )
        assert token_data(tokens) == ("word", None, "word")

    def test_escaped_letters_building_words(self):
        tokens = list(MTextParser(r"\\\{\} \\\{\}"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.SPACE,
            TokenType.WORD,
        )
        assert token_data(tokens) == (r"\{}", None, r"\{}")

    def test_invalid_escaped_letters_printed_verbatim(self):
        # The current implementation automatically end the previous word
        # at a backslash. Therefore "\:\;" returns two tokens!
        w1 = r"\:"
        w2 = r"\;"
        tokens = list(MTextParser(w1 + w2))
        t0, t1 = tokens
        assert t0.type is TokenType.WORD
        assert t0.data == w1
        assert t1.type is TokenType.WORD
        assert t1.data == w2

    def test_single_new_paragraph_token(self):
        tokens = list(MTextParser(r"\P"))
        assert token_types(tokens) == (TokenType.NEW_PARAGRAPH,)

    def test_new_paragraph_token_in_usual_context(self):
        tokens = list(MTextParser(r"word\Pword"))
        assert token_types(tokens) == (
            TokenType.WORD,
            TokenType.NEW_PARAGRAPH,
            TokenType.WORD,
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

    @pytest.mark.parametrize("char", list("AIJMZ"))
    def test_replace_all_caret_encoded_chars_by_space(self, char):
        # AutoCAD/BricsCAD preserve "^I" as tabulator, but this makes no sense
        # in a stacking expression and would add an unnecessary "if" check.
        token = list(MTextParser(f"\\S\\^{char}^ 2;"))[0]
        assert token.data == (" ", "2", "^")

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
        assert token.data == ("1^2", "", "")

    def test_escape_caret_new_line(self):
        token = list(MTextParser("\\S\\^J^ 2;"))[0]
        assert token.data == (" ", "2", "^")

    def test_remove_backslash_escape_char(self):
        token = list(MTextParser("\\S\\N^ \\P;"))[0]
        assert token.data == ("N", "P", "^")

    def test_preserve_second_stacking_type_char(self):
        token = list(MTextParser("\\S1/2/3;"))[0]
        assert token.data == ("1", "2/3", "/")
        token = list(MTextParser("\\S1#2/3;"))[0]
        assert token.data == ("1", "2/3", "#")

    def test_preserve_second_caret_char(self):
        token = list(MTextParser("\\S1^ 2^ 3;"))[0]
        assert token.data == ("1", "2^3", "^")

    def test_parse_without_stacking_type_char(self):
        token = list(MTextParser("\\S123;"))[0]
        assert token.data == ("123", "", "")

    def test_next_word_after_stacking(self):
        tokens = list(MTextParser("\\S1/2;word"))
        assert token_types(tokens) == (TokenType.STACK, TokenType.WORD)
        assert tokens[1].data == "word"

    def test_next_semi_colon_after_stacking(self):
        tokens = list(MTextParser("\\S1/2;;"))
        assert token_types(tokens) == (TokenType.STACK, TokenType.WORD)
        assert tokens[1].data == ";"

    @pytest.mark.parametrize(
        "expr",
        [
            r"word\p______;word",
            r"word\f______;word",
            r"word\F______;word",
        ],
    )
    def test_extraction_of_expression(self, expr):
        tokens = list(MTextParser(expr))
        assert token_types(tokens) == (TokenType.WORD, TokenType.WORD)
        assert token_data(tokens) == ("word", "word")


class TestMTextContextParsing:
    def test_switch_underline_on(self):
        tokens = list(MTextParser(r"\Lword"))
        assert len(tokens) == 1, "property changes should not yield tokens"
        assert tokens[0].ctx.underline is True

    def test_switch_underline_on_off_for_multiple_words(self):
        tokens = list(MTextParser(r"\Lword\l \Lword\l \Lword\l"))
        assert len(tokens) == 5
        assert tokens[0].ctx.underline is True
        assert tokens[1].ctx.underline is False
        assert tokens[2].ctx.underline is True
        assert tokens[3].ctx.underline is False
        assert tokens[4].ctx.underline is True

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
        assert t0.ctx.underline is True
        assert t1.ctx.underline is False
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

    @pytest.mark.parametrize(
        "s,e,attr",
        [
            ["\\L", "\\l", "underline"],
            ["\\K", "\\k", "strike_through"],
            ["\\O", "\\o", "overline"],
        ],
    )
    def test_switch_stroke_on_off_multiple_times(self, s, e, attr):
        text = s + "word word" + e + " " + s + "word word" + e + " word"
        # t[x]      0   12            3         4   56            78
        mp = MTextParser(text)

        assert [getattr(t.ctx, attr) for t in mp] == [
            True,  # 0
            True,  # 1
            True,  # 2
            False,  # 3
            True,  # 4
            True,  # 5
            True,  # 6
            False,  # 7
            False,  # 8
        ]

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

    def test_font_b0_i0(self):
        t0 = list(MTextParser(r"\fArial Narrow;word"))[0]
        font_face = t0.ctx.font_face
        assert font_face.family == "Arial Narrow"
        assert font_face.style == "normal"
        assert font_face.weight == "normal"

    def test_font_b1_i0(self):
        t0 = list(MTextParser(r"\fArial Narrow|b1;word"))[0]
        assert t0.ctx.font_face.weight == "bold"

    def test_font_b0_i1(self):
        t0 = list(MTextParser(r"\fArial Narrow|i1;word"))[0]
        assert t0.ctx.font_face.style == "italic"

    def test_font_b1_i1(self):
        t0 = list(MTextParser(r"\fArial Narrow|i1|b1;word"))[0]
        assert t0.ctx.font_face.style == "italic"
        assert t0.ctx.font_face.weight == "bold"

    def test_font_uppercase_command(self):
        t0 = list(MTextParser(r"\FArial Narrow;word"))[0]
        assert t0.ctx.font_face.family == "Arial Narrow"

    def test_empty_font_command_does_not_change_font_properties(self):
        t0, t1 = list(MTextParser(r"\fArial;word\f;word"))
        assert t0.ctx.font_face.family == "Arial"
        assert t0.ctx.font_face is t1.ctx.font_face

    def test_empty_font_family_name_does_not_change_font_properties(self):
        t0, t1 = list(MTextParser(r"\fArial;word\f|b1|i1;word"))
        assert t0.ctx.font_face.family == "Arial"
        assert t0.ctx.font_face is t1.ctx.font_face

    @pytest.mark.parametrize(
        "expr",
        [
            r"\H3",
            r"\H3;",
            r"\H+3",
            r"\H+3;",
            r"\H-3",  # ignore sign
            r"\H-3;",  # ignore sign
            r"\H0.3e1",
            r"\H0.3e1;",
            r"\H30e-1",
            r"\H30e-1;",
        ],
    )
    def test_absolut_height_command(self, expr):
        t0 = list(MTextParser(f"{expr}word"))[0]
        assert t0.ctx.cap_height == 3

    @pytest.mark.parametrize(
        "expr",
        [
            r"\H3x",
            r"\H3x;",
            r"\H+3x",
            r"\H+3x;",
            r"\H-3x",  # ignore sign
            r"\H-3x;",  # ignore sign
            r"\H0.3e1x",
            r"\H0.3e1x;",
            r"\H30e-1x",
            r"\H30e-1x;",
        ],
    )
    def test_relative_height_command(self, expr):
        t1 = list(MTextParser(rf"\H2;word{expr}word"))[1]
        assert t1.ctx.cap_height == 6.0
        assert t1.data == "word"

    @pytest.mark.parametrize(
        "expr",
        [
            r"\H",
            r"\H;",
            r"\Hx",
            r"\Hx;",
            r"\H1-2;",
            r"\H.3",  # this does work in AutoCAD
            r"\H.3;",  # this does work in AutoCAD
            r"\H.3x",  # this does work in AutoCAD
            r"\H.3x;",  # this does work in AutoCAD
            r"\H.",
            r"\H.;",
        ],
    )
    def test_invalid_height_command(self, expr):
        t0 = list(MTextParser(rf"{expr}word"))[0]
        assert t0.ctx.cap_height == 1.0
        # The important part: does not raise an exception, the word after the
        # INVALID height command is not relevant and may differ from AutoCAD and
        # BricsCAD rendering.

    @pytest.mark.parametrize(
        "expr",
        [
            r"\W3",
            r"\W3;",
            r"\W+3",
            r"\W+3;",
            r"\W-3",  # ignore sign
            r"\W-3;",  # ignore sign
            r"\W0.3e1",
            r"\W0.3e1;",
            r"\W30e-1",
            r"\W30e-1;",
        ],
    )
    def test_absolut_width_command(self, expr):
        t0 = list(MTextParser(f"{expr}word"))[0]
        assert t0.ctx.width_factor == 3

    @pytest.mark.parametrize(
        "expr",
        [
            r"\W3x",
            r"\W3x;",
            r"\W+3x",
            r"\W+3x;",
            r"\W-3x",  # ignore sign
            r"\W-3x;",  # ignore sign
            r"\W0.3e1x",
            r"\W0.3e1x;",
            r"\W30e-1x",
            r"\W30e-1x;",
        ],
    )
    def test_relative_height_command(self, expr):
        t1 = list(MTextParser(rf"\W2;word{expr}word"))[1]
        assert t1.ctx.width_factor == 6.0
        assert t1.data == "word"

    @pytest.mark.parametrize(
        "expr",
        [
            r"\T3",
            r"\T3;",
            r"\T+3",
            r"\T+3;",
            r"\T-3",  # ignore sign
            r"\T-3;",  # ignore sign
            r"\T0.3e1",
            r"\T0.3e1;",
            r"\T30e-1",
            r"\T30e-1;",
        ],
    )
    def test_absolut_char_tracking_command(self, expr):
        t0 = list(MTextParser(f"{expr}word"))[0]
        assert t0.ctx.char_tracking_factor == 3

    @pytest.mark.parametrize(
        "expr",
        [
            r"\T3x",
            r"\T3x;",
            r"\T+3x",
            r"\T+3x;",
            r"\T-3x",  # ignore sign
            r"\T-3x;",  # ignore sign
            r"\T0.3e1x",
            r"\T0.3e1x;",
            r"\T30e-1x",
            r"\T30e-1x;",
        ],
    )
    def test_relative_char_tracking_command(self, expr):
        t1 = list(MTextParser(rf"\T2;word{expr}word"))[1]
        assert t1.ctx.char_tracking_factor == 6.0
        assert t1.data == "word"

    @pytest.mark.parametrize(
        "expr",
        [
            r"\Q3",
            r"\Q3;",
            r"\Q+3",
            r"\Q+3;",
            r"\Q0.3e1",
            r"\Q0.3e1;",
            r"\Q30e-1",
            r"\Q30e-1;",
        ],
    )
    def test_positive_oblique_command(self, expr):
        t0 = list(MTextParser(f"{expr}word"))[0]
        assert t0.ctx.oblique == 3

    @pytest.mark.parametrize(
        "expr",
        [
            r"\Q-3",
            r"\Q-3;",
            r"\Q-0.3e1",
            r"\Q-0.3e1;",
            r"\Q-30e-1",
            r"\Q-30e-1;",
        ],
    )
    def test_negative_oblique_command(self, expr):
        t0 = list(MTextParser(f"{expr}word"))[0]
        assert t0.ctx.oblique == -3

    @pytest.mark.parametrize(
        "expr",
        [
            r"\C3",
            r"\C3;",
            r"\C03",
            r"\C03;",
        ],
    )
    def test_aci_color(self, expr):
        t0 = list(MTextParser(rf"{expr}word"))[0]
        assert t0.ctx.aci == 3
        assert t0.ctx.rgb is None

    @pytest.mark.parametrize(
        "expr",
        [
            r"\C1000",
            r"\C1000;",
        ],
    )
    def test_aci_color_is_limited_to_256(self, expr):
        t0 = list(MTextParser(rf"{expr}word"))[0]
        assert t0.ctx.aci == 7  # default value
        assert t0.ctx.rgb is None
        assert t0.data == "word"

    @pytest.mark.parametrize(
        "expr",
        [
            r"\c255",
            r"\c255;",
            r"\c0255",
            r"\c0255;",
        ],
    )
    def test_rgb_color(self, expr):
        t0 = list(MTextParser(rf"{expr}word"))[0]
        assert t0.ctx.aci == 7  # default value
        assert t0.ctx.rgb == (255, 0, 0)

    def test_rgb_color_overflow(self):
        t0 = list(MTextParser(r"\c9999999999;word"))[0]
        assert t0.ctx.rgb == (255, 227, 11)


class TestMTextParagraphProperties:
    @pytest.mark.parametrize(
        "expr, expected",
        [
            ("i0;", 0),
            ("i+1;", 1),
            ("i1.1;", 1.1),
            ("i-1;", -1),
            ("i-1.1;", -1.1),
        ],
    )
    def test_indent_first_line(self, expr, expected):
        t0 = list(MTextParser(rf"\p{expr}word"))[0]
        assert t0.ctx.paragraph.indent == expected

    @pytest.mark.parametrize(
        "expr, expected",
        [
            ("l0;", 0),
            ("l+1;", 1),
            ("l1.1;", 1.1),
            ("l-1;", -1),
            ("l-1.1;", -1.1),
        ],
    )
    def test_indent_left(self, expr, expected):
        t0 = list(MTextParser(rf"\p{expr}word"))[0]
        assert t0.ctx.paragraph.left == expected

    @pytest.mark.parametrize(
        "expr, expected",
        [
            ("r0;", 0),
            ("r+1;", 1),
            ("r1.1;", 1.1),
            ("r-1;", -1),
            ("r-1.1;", -1.1),
        ],
    )
    def test_indent_right(self, expr, expected):
        t0 = list(MTextParser(rf"\p{expr}word"))[0]
        assert t0.ctx.paragraph.right == expected

    @pytest.mark.parametrize(
        "expr, expected",
        [
            ("ql;", MTextParagraphAlignment.LEFT),
            ("qr;", MTextParagraphAlignment.RIGHT),
            ("qc;", MTextParagraphAlignment.CENTER),
            ("qj;", MTextParagraphAlignment.JUSTIFIED),
            ("qd;", MTextParagraphAlignment.DISTRIBUTED),
            ("q?;", MTextParagraphAlignment.DEFAULT),
        ],
    )
    def test_paragraph_alignment(self, expr, expected):
        t0 = list(MTextParser(rf"\p{expr}word"))[0]
        assert t0.ctx.paragraph.align == expected

    def test_tab_stops(self):
        t0 = list(MTextParser(r"\pxt4,c5,r6,7.5;word"))[0]
        assert t0.ctx.paragraph.tab_stops == (4, "c5", "r6", 7.5)

    @pytest.mark.parametrize(
        "expr",
        [
            "i1,l2,r3,qc,t1,2,3;",  # regular order
            "qc,l2,r3,i1,t1,2,3;",  # tab stops have to be the last argument
            "xqc,xl2,xr3,xi1,xt1,2,3;",  # ignore "x"
            "xqcl2xr3xi1xt1,2,3;",  # ezdxf: commas not required between arguments
        ],
    )
    def test_combinations(self, expr):
        t0 = list(MTextParser(rf"\p{expr}word"))[0]
        assert t0.ctx.paragraph == (
            1,
            2,
            3,
            MTextParagraphAlignment.CENTER,
            (1, 2, 3),
        )

    def test_reset_arguments(self):
        t0, t1 = list(
            MTextParser(r"\pi1,l2,r3,qc,t1,2,3;word\pi*,l*,r*,q*,t;word")
        )
        assert t0.ctx.paragraph == (
            1,
            2,
            3,
            MTextParagraphAlignment.CENTER,
            (1, 2, 3),
        )
        assert t1.ctx.paragraph == ParagraphProperties()  # reset to default

    def test_invalid_tab_stops(self):
        tokens = list(MTextParser(r"\pi0,l0,tz;A"))
        t = tokens[0]
        assert t.ctx.paragraph.tab_stops == tuple()


if __name__ == "__main__":
    pytest.main([__file__])
