#  License: MIT License

import pytest
import ezdxf
from ezdxf.addons import MTextExplode
from ezdxf.render.abstract_mtext_renderer import split_cjk_word

CJK_TEXT = (
    "這是一段沒有空格的中文文字用來測試多行文字在指定寬度時是否會自動換行而不是超出邊界"
)


def test_split_cjk_word():
    assert split_cjk_word("中文字") == ["中", "文", "字"]
    assert split_cjk_word("ABC") == ["ABC"]
    assert split_cjk_word("ABC中文") == ["ABC", "中", "文"]
    # no line starts with closing punctuation or ends with opening punctuation
    assert split_cjk_word("中文，「字」") == ["中", "文，", "「字」"]


def test_explode_wraps_cjk_text():
    doc = ezdxf.new()
    msp = doc.modelspace()
    mtext = msp.add_mtext(CJK_TEXT)
    mtext.dxf.char_height = 0.2
    mtext.dxf.width = 4.75

    with MTextExplode(msp) as explode:
        explode.explode(mtext, destroy=True)

    texts = msp.query("TEXT")
    lines = {round(e.dxf.insert.y, 6) for e in texts}
    assert len(lines) > 1
    assert "".join(e.dxf.text for e in texts) == CJK_TEXT


if __name__ == "__main__":
    pytest.main([__file__])
