# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License

from ezdxf.lldxf.tags import text_to_multi_tags, multi_tags_to_text

TEST_TEXT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, 
sed diam nonumy eirmod tempor invidunt ut labore et dolore 
magna aliquyam erat, sed diam voluptua. At vero eos et accusam 
et justo duo dolores et ea rebum. Stet clita kasd 
gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. 
Lorem ipsum dolor sit amet, consetetur sadipscing 
elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna 
aliquyam erat, sed diam voluptua. At vero 
eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea 
takimata sanctus est Lorem ipsum dolor sit amet.
"""


def test_text_to_multi_tags():
    tags = text_to_multi_tags(TEST_TEXT, code=303, size=40)
    assert len(tags) == 16
    assert tags[0].code == 303
    assert len(tags[0].value) == 40

    text = multi_tags_to_text(tags)
    assert text == TEST_TEXT
