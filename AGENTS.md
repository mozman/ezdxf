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

## Documentation language (Simplified Technical English)

New prose, in docstrings and in `docs/source`, uses Simplified Technical
English (STE100) in spirit, not strictly. Existing text is migrated step by
step by the maintainer: do not restyle existing documentation as a side effect
of another change.

- Active voice and simple present tense; imperative for instructions. Passive
  voice is fine when the actor is unknown or irrelevant ("a `DXFError` is
  raised").
- One idea per sentence. Target 20 words in procedures and 25 words in
  descriptions.
- One topic per paragraph, six sentences at most.
- `must` for requirements, `can` for permission, possibility or failure
  ("can raise `DXFError`", "the attribute can be `None`"). Remove `should`,
  `may`, `might`, `could` and `would` unless the sentence loses accuracy.
- One term for one concept. Reuse the names that the code uses and the terms in
  `docs/source/develop/doc_formatting_guide.rst`, and qualify an ambiguous word
  ("Python attribute" vs "DXF ATTRIB entity"). Do not add synonyms.
- No contractions, slang, idioms or humor, and no filler words: `simply`,
  `just`, `easy`, `obviously`, `basically`, `note that`, `it is important to`.
  Write complete sentences with articles.
- Use a vertical list for three or more parallel items or steps.
- These rules never override accuracy or Sphinx markup. Identifiers, DXF names
  and type names are not dictionary words.

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