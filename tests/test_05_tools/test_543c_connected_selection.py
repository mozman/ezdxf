from __future__ import annotations


import random


import ezdxf


from ezdxf import bbox, select


from ezdxf.math import BoundingBox2d


def reference_bbox_chained(start, entities):
    """Original input-order scanning behavior, including discovery order."""
    boxes = {e: BoundingBox2d(bbox.extents([e], fast=True)) for e in entities}
    selected = {start: BoundingBox2d(bbox.extents([start], fast=True))}
    restart = True
    while restart:
        restart = False
        for entity in entities:
            if entity not in selected and any(
                boxes[entity].has_overlap(box) for box in selected.values()
            ):
                selected[entity] = boxes[entity]
                restart = True
    return list(selected)


def test_chained_selection_preserves_discovery_order_with_duplicate_inputs():
    rng = random.Random(543)
    for _ in range(50):
        layout = ezdxf.new().modelspace()
        for _ in range(20):
            x, y = rng.randrange(10), rng.randrange(10)
            layout.add_line((x, y, rng.randrange(10)), (x + 2, y + 2, 100))
        entities = list(layout)
        start = rng.choice(entities)
        entities.extend(rng.choices(entities, k=8))
        rng.shuffle(entities)
        expected = reference_bbox_chained(start, entities)
        assert list(select.bbox_chained(start, iter(entities))) == expected


def test_chained_selection_empty_start_and_unsupported_entities():
    layout = ezdxf.new().modelspace()
    line = layout.add_line((0, 0), (1, 1))
    ray = layout.add_ray((0, 0), (1, 0))
    assert list(select.bbox_chained(ray, [line, ray])) == [ray]
    assert list(select.bbox_chained(line, [ray])) == [line]


def test_chained_selection_ignores_z_and_includes_start_outside_input():
    layout = ezdxf.new().modelspace()
    start = layout.add_line((0, 0, -50), (1, 0, -50))
    near = layout.add_line((1, 0, 50), (2, 0, 50))
    far = layout.add_line((10, 0), (11, 0))
    assert list(select.bbox_chained(start, [far, near, near])) == [start, near]


def test_reversed_chain_checks_each_pair_at_most_once(monkeypatch):
    layout = ezdxf.new().modelspace()
    for x in range(40):
        layout.add_line((x, 0), (x + 1, 0))
    calls = 0
    original = BoundingBox2d.has_overlap

    def count_overlap(self, other):
        nonlocal calls
        calls += 1
        return original(self, other)

    monkeypatch.setattr(BoundingBox2d, "has_overlap", count_overlap)
    assert len(select.bbox_chained(layout[-1], layout)) == 40
    assert calls <= 40 * 39 // 2
