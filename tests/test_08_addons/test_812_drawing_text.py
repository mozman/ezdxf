from ezdxf.addons.drawing.text import _split_multiline_text


def test_word_wrapping():
    def get_text_width(s: str) -> float:
        return len(s)

    assert _split_multiline_text('', 0, get_text_width) == []
    assert _split_multiline_text('   \n    ', 1, get_text_width) == []

    assert _split_multiline_text('abc', 0, get_text_width) == ['abc']
    assert _split_multiline_text(' abc', 6, get_text_width) == [' abc']
    assert _split_multiline_text('abc ', 1, get_text_width) == ['abc']
    assert _split_multiline_text(' abc ', 6, get_text_width) == [' abc']

    assert _split_multiline_text('abc\ndef', 1, get_text_width) == ['abc', 'def']
    assert _split_multiline_text('   abc\ndef', 1, get_text_width) == ['', 'abc', 'def']
    assert _split_multiline_text('   abc\ndef', 6, get_text_width) == ['   abc', 'def']
    assert _split_multiline_text('abc    \n    def', 1, get_text_width) == ['abc', 'def']

    assert _split_multiline_text(' a ', 1, get_text_width) == ['', 'a']
    assert _split_multiline_text('\na ', 2, get_text_width) == ['', 'a']
    assert _split_multiline_text(' \na ', 1, get_text_width) == ['', 'a']
    assert _split_multiline_text(' \n \n ', 1, get_text_width) == []
    assert _split_multiline_text(' \n \n a', 1, get_text_width) == ['', '', 'a']

    assert _split_multiline_text('  abc', 6, get_text_width) == ['  abc']
    assert _split_multiline_text('  abc def', 6, get_text_width) == ['  abc', 'def']
    assert _split_multiline_text('  abc def  ', 6, get_text_width) == ['  abc', 'def']
    assert _split_multiline_text('  abc def', 1, get_text_width) == ['', 'abc', 'def']
    assert _split_multiline_text('  abc def', 6, get_text_width) == ['  abc', 'def']
