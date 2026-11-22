# Copyright (c) 2026, 1915rising
# License: MIT License
"""Regression tests for issue #1484.

Pylance/pyright reported ``reportPrivateImportUsage`` for the public
top-level API (e.g. ``ezdxf.new()``) because the names re-exported by
``ezdxf/__init__.py`` were not declared as exported.  Per the typing
spec, an imported name is public if it is listed in ``__all__`` (or
imported with a redundant alias).  These tests guard the ``__all__``
declaration so new re-exports cannot silently become "private" again.
"""
import ast
import pathlib

import ezdxf


def imported_names() -> set[str]:
    """All names imported into ezdxf/__init__.py via 'from ... import ...'."""
    source = pathlib.Path(ezdxf.__file__).read_text(encoding="utf-8")
    names: set[str] = set()
    for node in ast.parse(source).body:  # module level only, not function bodies
        if isinstance(node, ast.ImportFrom) and node.module != "typing":
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def test_all_exported_names_exist() -> None:
    for name in ezdxf.__all__:
        assert hasattr(ezdxf, name), f"ezdxf.__all__ lists missing name {name!r}"


def test_imported_names_are_exported() -> None:
    missing = {
        name
        for name in imported_names()
        if not name.startswith("_") or name == "__version__"
    } - set(ezdxf.__all__)
    assert missing == set(), f"imported but not exported: {sorted(missing)}"


def test_documented_public_names_are_exported() -> None:
    for name in ("new", "read", "readfile", "options", "DXFError", "InsertUnits"):
        assert name in ezdxf.__all__


if __name__ == "__main__":
    test_all_exported_names_exist()
    test_imported_names_are_exported()
    test_documented_public_names_are_exported()
