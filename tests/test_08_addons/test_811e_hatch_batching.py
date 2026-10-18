import pytest


import ezdxf


from ezdxf.math import Vec2


from ezdxf.addons.drawing import RenderContext, Frontend


from ezdxf.addons.drawing.properties import Properties


from ezdxf.addons.drawing.debug_backend import BasicBackend


class MyTestFrontend(Frontend):
    def __init__(self, ctx, backend):
        super().__init__(ctx, backend)
        self.out = backend


@pytest.fixture
def doc():
    d = ezdxf.new()
    d.layers.new("Test1")
    d.styles.add("DEJAVU", font="DejaVuSans.ttf")
    return d


@pytest.fixture
def msp(doc):
    return doc.modelspace()


@pytest.fixture
def ctx(doc):
    return RenderContext(doc)


@pytest.fixture
def basic(doc, ctx):
    return MyTestFrontend(ctx, BasicBackend())


@pytest.mark.parametrize(
    "batch_size,expected_sizes",
    [
        (None, [2500]),
        (1024, [1024, 1024, 452]),
    ],
)
def test_hatch_pattern_output_is_batched(
    msp, basic, monkeypatch, batch_size, expected_sizes
):
    from ezdxf.render import hatching

    baseline = hatching.HatchBaseLine(Vec2(), Vec2(1, 0), Vec2(0, 1), [1, -1])
    monkeypatch.setattr(
        hatching, "pattern_baselines", lambda *args, **kwargs: [baseline]
    )
    monkeypatch.setattr(
        hatching,
        "hatch_paths",
        lambda *args, **kwargs: [hatching.Line(Vec2(), Vec2(5000, 0), 0)],
    )
    hatch = msp.add_hatch()
    hatch.set_pattern_fill("ANSI31")
    basic.config = basic.config.with_changes(hatching_batch_size=batch_size)
    batches = []
    monkeypatch.setattr(
        basic.pipeline,
        "draw_solid_lines",
        lambda lines, properties: batches.append(list(lines)),
    )
    basic.draw_hatch_pattern(hatch, [], Properties())
    assert [len(batch) for batch in batches] == expected_sizes
    flattened = [segment for batch in batches for segment in batch]
    for index, (start, end) in enumerate(flattened):
        assert start == Vec2(index * 2, 0)
        assert end == Vec2(index * 2 + 1, 0)
