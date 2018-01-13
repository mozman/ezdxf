import pytest

from ezdxf.tools.complex_ltype import lin_tokenizer, lin_parser, lin_compiler


def test_line_type_tokenizer_just_numbers():
    ltype = 'A,.25,-.125,.25,-.125,0,-.125'
    result = list(lin_tokenizer(ltype))
    assert result == ['A', '.25', '-.125', '.25', '-.125', '0', '-.125']


def test_line_type_tokenizer_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = list(lin_tokenizer(ltype))
    assert result == ['A', '.5', '-.2', '["GAS"', 'STANDARD', 'S=.1', 'U=0.0', 'X=-0.1', 'Y=-.05]', '-.25']


def test_line_type_tokenizer_string_with_comma():
    ltype = 'A, "TEXT, TEXT", 0'
    result = list(lin_tokenizer(ltype))
    assert result == ['A', '"TEXT, TEXT"', '0']


def test_line_type_tokenizer_shapes():
    ltype = 'A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1'
    result = list(lin_tokenizer(ltype))
    assert result == ['A', '.25', '-.1', '[BOX', 'ltypeshp.shx', 'x=-.1', 's=.1]', '-.1', '1']


def test_line_type_parser_just_numbers():
    ltype = 'A,.25,-.125,.25,-.125,0,-.125'
    result = lin_parser(ltype)
    assert result == ['A', .25, -.125, .25, -.125, 0, -.125]


def test_line_type_parser_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = lin_parser(ltype)
    assert result == ['A', .5, -.2, ['TEXT', 'GAS', 'STANDARD', 's', .1, 'u', 0.0, 'x', -0.1, 'y', -.05], -.25]


def test_line_type_parser_shape():
    ltype = 'A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1'
    result = lin_parser(ltype)
    assert result == ['A', .25, -.1, ['SHAPE', 'BOX', 'ltypeshp.shx', 'x', -.1, 's', .1], -.1, 1]


def test_lin_compiler_floats():
    ltype = 'A,.25,-.125,.25,-.125,0,-.125'
    result = lin_compiler(ltype)
    assert result == [(49, .25), (49, -.125), (49, .25), (49, -.125), (49, 0), (49, -.125)]


def test_lin_compiler_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = lin_compiler(ltype)
    assert result[0] == (49, .5)
    assert result[1] == (49, -.2)
    text = result[2]
    assert text.type == 'TEXT'
    assert text.text == 'GAS'
    assert text.font == 'STANDARD'
    assert text.tags[0] == (46, .1)
    assert text.tags[1] == (50, 0)
    assert text.tags[2] == (44, -0.1)
    assert text.tags[3] == (45, -0.05)
    assert result[3] == (49, -.25)


def test_lin_compiler_shape():
    ltype = 'A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1'
    result = lin_compiler(ltype)
    assert result[0] == (49, .25)
    assert result[1] == (49, -.1)
    text = result[2]
    assert text.type == 'SHAPE'
    assert text.text == 'BOX'
    assert text.font == 'ltypeshp.shx'
    assert text.tags[0] == (44, -.1)
    assert text.tags[1] == (46, .1)
    assert result[3] == (49, -.1)
    assert result[4] == (49, 1)


if __name__ == '__main__':
    pytest.main([__file__])

