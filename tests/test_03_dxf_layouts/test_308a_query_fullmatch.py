import pytest


from ezdxf.query import EntityQuery


from ezdxf.entities import MText


@pytest.mark.parametrize(
    "pattern, value, matches",
    [
        ("foo|bar", "foobar", False),
        ("foo|bar", "foo", True),
        ("foo|bar", "bar", True),
        ("(foo|(bar|baz))", "barbaz", False),
        (r"foo\$", "foo$", True),
        (r"foo\$", "foo$extra", False),
        ("(?i)foo|bar", "BAR", True),
        ("(?-i:FOO)", "FOO", True),
        ("(?-i:FOO)", "foo", False),
        ("foo", "foo\n", False),
        ("foo$", "foo\n", False),
        ("(?s)foo.*", "foo\n", True),
    ],
)
@pytest.mark.parametrize("ignore_case", [True, False])
def test_regex_matches_entire_attribute(pattern, value, matches, ignore_case):
    # MTEXT preserves newlines; TEXT and layer names strip them.
    entity = MText.new(dxfattribs={"text": value})
    assert entity.dxf.text == value
    query = EntityQuery([entity])["text"]
    query.ignore_case = ignore_case
    assert bool(query.match(pattern)) is matches
    suffix = "i" if ignore_case else ""
    assert bool(EntityQuery([entity], f'MTEXT[text ? "{pattern}"]{suffix}')) is matches
    assert (
        bool(EntityQuery([entity], f'MTEXT[text !? "{pattern}"]{suffix}'))
        is not matches
    )
