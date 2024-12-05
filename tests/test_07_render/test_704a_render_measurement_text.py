# Copyright (c) 2024 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import Modelspace


@pytest.fixture(scope="module")
def msp() -> Modelspace:
    doc = ezdxf.new("R2007", setup=True)
    return doc.modelspace()


@pytest.mark.parametrize("text", ["", "<>"])
def test_regular_measurement_text(msp, text):
    dim = msp.add_linear_dim(
        base=(0, 2),
        p1=(0, 0),
        p2=(3, 0),
    )
    dim.set_text(text)

    block = dim.render().geometry.layout
    mtext = block.query("MTEXT").first
    assert mtext.text == "300"


def test_suppress_measurement_text(msp):
    dim = msp.add_linear_dim(
        base=(0, 2),
        p1=(0, 0),
        p2=(3, 0),
    )
    dim.set_text(" ")

    block = dim.render().geometry.layout
    assert len(block.query("MTEXT")) == 0  # no MTEXT entity expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("<>", "300"),
        ("Ø <>", "Ø 300"),
        ("<> cm", "300 cm"),
        ("[ <> ]", "[ 300 ]"),
        ("<> <>", "300 <>"),  # only the first "<>" will be replaced
    ],
)
def test_override_measurement_text(msp, text, expected):
    dim = msp.add_linear_dim(
        base=(0, 2),
        p1=(0, 0),
        p2=(3, 0),
    )
    dim.set_text(text)

    block = dim.render().geometry.layout
    mtext = block.query("MTEXT").first
    assert mtext.text == expected


if __name__ == "__main__":
    pytest.main([__file__])
