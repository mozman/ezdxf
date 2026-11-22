# AGENTS.md

Guidance for AI coding agents. The code is the authority: where this file or the
documentation disagrees with the source, follow the source.

Human-facing conventions live in the docs, read them before writing code or
documentation:

- `docs/source/develop/index.rst` - black formatting (88 cols), mypy usage
- `docs/source/develop/doc_formatting_guide.rst` - docstring markup, inline
  code, `(internal API)` markers, terminology (DXF types, 2D/3D, axis names)

## Validation

- Tests: `python -m pytest tests/<group>/test_<name>.py -q`; full suite:
  `pytest tests integration_tests`.
- Type check: `mypy --ignore-missing-imports -p ezdxf`. Do not use `--strict`:
  strict type checking is not required and making the package strict-clean is
  not a goal.
- `.venv/`, `makefile` and `tox.ini` are untracked local files, so root `make`
  targets exist only if a `makefile` was created from `makefile.template`.

## Docstrings

- Google style parsed by `sphinx.ext.napoleon`. Sections in use: `Args:`,
  `Returns:`, `Raises:`, `Attributes:`; `Yields:` is fine for generators.
- New modules start with the MIT license header used across the package.

## Documentation pages (`docs/source`)

- Most pages use `.. module::` with `.. autofunction::` / `.. autoclass::`
  rather than `.. automodule::`, so a module docstring may not show up on its
  page.
- Do not add `.. py:attribute:: name` for a name already listed in a class
  docstring `Attributes:` section - Sphinx reports "duplicate object
  description".
- Build from `docs/`, with `sphinx-build` on `PATH`:

  ```
  # POSIX
  EZDXF_DISABLE_C_EXT=1 sphinx-build -b html -d build/doctrees source build/html
  # PowerShell
  $env:EZDXF_DISABLE_C_EXT='1'; sphinx-build -b html -d build/doctrees source build/html
  ```

  The variable is required, otherwise the Cython classes replace the Python
  classes and lose their docstrings; only `1` or `True` are accepted.
- Incremental builds may skip an edited `.rst`; touch the file before judging
  warnings.
- Prose examples have drifted from the API before - verify signatures.